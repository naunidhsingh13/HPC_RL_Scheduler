def step(action):
    job = action
    if start_job(job):
        return _next_observation()
    else:
        if backfill == false:
            backfill = true
            reserved_job = job
            return _next_observation()

    scan_event()
    return _next_observation()

def start_job(job):
    if system_available(job):
        start(job)
        return True

    return False

def _next_observation():
    window = get_wait_queue()

    if backfill:
        window = get_backfill_candidates(window)

    resources = get_system_resources()

    features = get_features(window, resources)
    return features

def scan_event():
    while len(event_seq) > 0 && is_monitor(event_seq[0]) == true:
        event_monitor()
        del event_seq[0]

    if len(event_seq) == 0:
        import_submit_events()

    event_job(event_seq[0])
    return None

def event_job(event):
    if submit_event(event):
        submit(event.job)
    else:
        finish(event.job)
        if start_job(reserved_job):
            reserved_job = 0
            backfill = false