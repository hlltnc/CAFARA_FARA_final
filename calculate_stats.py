def calculate_stats(success_count, drop_count):
    total_requests = success_count + drop_count

    if total_requests == 0:
        print("⚠️ Hiç request işlenmedi.")
        return 0.0, 0.0

    success_rate = (success_count / total_requests) * 100
    drop_rate = 100 - success_rate

    print(f"📊 Request Processing Summary")
    print(f"   ✔️ Successful Requests: {success_count}")
    print(f"   ❌ Dropped Requests: {drop_count}")
    print(f"   ✅ Success Rate: {success_rate:.2f}%")
    print(f"   ❌ Drop Rate:    {drop_rate:.2f}%")

    return success_rate, drop_rate