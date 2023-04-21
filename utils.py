from models import LogDb, session, TaskChecker, config_class
from datetime import datetime
from email.message import EmailMessage
import smtplib


def add_log_db(project, task, issue, description, msg_type):
    new_log_db = LogDb(
        project=project,
        task=task,
        issue=issue,
        description=description,
        msg_type=msg_type
    )
    session.add(new_log_db)
    session.commit()


def task_checker_db(status, task_details, comment='', task_name='Get EMSX Trade', task_type='Task Scheduler'):
    if comment != '':
        comment_db = comment
    else:
        comment_db = 'Success'

    new_task_checker = TaskChecker(
        task_name=task_name,
        task_details=task_details,
        task_type=task_type,
        status=status,
        comment=comment_db
    )
    session.add(new_task_checker)
    session.commit()

    if status == 'Success':
        session.query(TaskChecker).filter(TaskChecker.task_details == task_details) \
            .filter(TaskChecker.status == 'Fail').filter(TaskChecker.active == 1).delete()
        session.commit()


def simple_email(subject, body, ml, html=None):

    mail = config_class.MAIL_USERNAME
    password = config_class.MAIL_PASSWORD

    msg = EmailMessage()
    msg['subject'] = subject
    msg['From'] = 'ananda.am.system@gmail.com'
    msg['To'] = ml  # multiple email: 'olivier@ananda-am.com, lekepi@gmail.com'
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(mail, password)
        smtp.send_message(msg)


def loop_checker(minutes=30):
    today = datetime.now()
    current_time = datetime.now().hour + datetime.now().minute / 60
    if current_time > 7.5 and today.weekday() < 5:
        loop_projects = ['Factset', 'Task Extra', 'Get Trade EMSX', 'PB NAV Reporting']
        today_dt = datetime(year=today.year, month=today.month, day=today.day)
        today_str = today.strftime('%Y-%m-%d')
        task_loop_db = session.query(TaskChecker).filter(TaskChecker.task_name == 'Loop').filter(TaskChecker.date_time>today_dt).all()
        log_loop_db = session.query(LogDb).filter(LogDb.task == 'Loop').\
            filter(LogDb.date_time > today_dt).order_by(LogDb.date_time.desc()).all()

        for project in loop_projects:
            task_loop_list = [task for task in task_loop_db if task.task_details == f'Loop {project} - {today_str}']
            if not task_loop_list:
                log_project_list = [log for log in log_loop_db if log.project == project]
                if log_project_list:
                    log_project = log_project_list[0]
                    # get the difference between log_project.date_time and now in minutes
                    minute_diff = int((datetime.now() - log_project.date_time).total_seconds() / 60)
                    if minute_diff > 30:
                        subject = f"ERROR - Loop '{project}' not working - {today_str}"
                        comment = f"'{project}' has not run for {int(minute_diff)} minutes, please contact Olivier"
                        task_checker_db('Fail', f'Loop {project} - {today_str}',
                                        comment=comment, task_name='Loop', task_type='Task Scheduler')
                        simple_email(subject, comment, config_class.MAIL_BO)
                else:
                    subject = f"ERROR - Loop '{project}' not working - {today_str}"
                    comment = f"'{project}' has not run at all today, please contact Olivier"
                    task_checker_db('Fail', f'Loop {project} - {today_str}',
                                    comment=comment, task_name='Loop', task_type='Task Scheduler')
                    simple_email(subject, comment, config_class.MAIL_BO)