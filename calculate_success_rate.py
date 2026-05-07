

def calculate_success_rate(success_count, drop_count):
    total_requests = success_count + drop_count

    if total_requests == 0:
        print("⚠️ Hiç request işlenmedi.")
        return 0.0  # Eksik olan yer burasıydı!

    success_rate = (success_count / total_requests) * 100
    print(f"📊 Request Success Rate: {success_rate:.2f}%")
    print("📊 Request Processing Summary")
    print(f"   ✔️ Successful Requests: {success_count}")
    print(f"   ❌ Dropped Requests: {drop_count}")
    print(f"   ✅ Success Rate: {success_rate:.2f}%")



    return success_rate