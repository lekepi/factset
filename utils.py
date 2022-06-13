from models import LogDb, session


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