# Loaded automatically by gunicorn from the working directory.


def post_worker_init(worker):
    # start the background jobs once the (single) worker is ready
    from app.scheduler import start_scheduler
    start_scheduler()
