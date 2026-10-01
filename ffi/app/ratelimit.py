from ipaddress import ip_address


def client_ip(request):
    candidates = [
        request.META.get("HTTP_X_REAL_IP"),
        request.META.get("REMOTE_ADDR"),
    ]

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    # Nginx appends the connecting address, so inspect this header right-to-left.
    candidates.extend(reversed(forwarded_for.split(",")))

    for candidate in candidates:
        candidate = (candidate or "").strip()
        try:
            return str(ip_address(candidate))
        except ValueError:
            continue

    # Keep malformed proxy metadata from turning a form submission into a 500.
    return "0.0.0.0"
