def record_result(results, success, elapsed_time, status_or_error):
    if success:
        results['success'] += 1
        results['times'].append(elapsed_time)
        results['status_codes'][status_or_error] = results['status_codes'].get(status_or_error, 0) + 1
    else:
        results['fail'] += 1
        results['errors'].append(status_or_error)

def print_summary(results):
    total = results['success'] + results['fail']
    avg_time = sum(results['times']) / len(results['times']) if results['times'] else 0

    print("\n📊 Load Test Summary")
    print("--------------------")
    print(f"Total Requests  : {total}")
    print(f"Successful       : {results['success']}")
    print(f"Failed           : {results['fail']}")
    print(f"Avg Response Time: {avg_time:.2f}s")
    print(f"Status Codes     : {results['status_codes']}")
    if results['errors']:
        print(f"\nErrors:\n--------")
        for err in results['errors']:
            print(f"❌ {err}")
