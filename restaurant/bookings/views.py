from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from hotels.views import Restaurant  


# --------------------------
# Add a new booking
# --------------------------
def book_table(request, hotel_id):
    hotel = next((h for h in restaurants if h['id'] == hotel_id), None)

    if request.method == "POST":
        name = request.POST.get("name")
        date = request.POST.get("date")
        time = request.POST.get("time")
        table_size = request.POST.get("table_size")

        # Create booking object
        new_booking = {
            "id": timezone.now().timestamp(), 
            "hotel_id": hotel["id"],
            "hotel_name": hotel["name"],
            "name": name,
            "date": date,
            "time": time,
            "table_size": table_size,
            "status": "confirmed",  
        }

        
        bookings = request.session.get("bookings", [])
        bookings.append(new_booking)

        
        request.session["bookings"] = bookings
        request.session.modified = True

        return redirect(reverse("bookings:booking_success"))

    return render(request, "bookings/book_table.html", {"hotel": hotel})


# --------------------------
# Success Page
# --------------------------
def booking_success(request):
    booking_data = request.session.get("bookings", [])[-1]  
    return render(request, "bookings/booking_success.html", {"booking": booking_data})


# --------------------------
# Bookings List (Upcoming + Past)
# --------------------------
def booking_list(request):
    bookings = request.session.get("bookings", [])
    today = timezone.now().date()

    upcoming = []
    past = []

    for b in bookings:
        booking_date = timezone.datetime.strptime(b["date"], "%Y-%m-%d").date()

        if booking_date >= today:
            upcoming.append(b)
        else:
            past.append(b)

    return render(request, "bookings/booking_list.html", {
        "upcoming": upcoming,
        "past": past,
    })


# --------------------------
# Cancel Booking
# --------------------------
def cancel_booking(request, booking_id):
    bookings = request.session.get("bookings", [])

    
    for b in bookings:
        if str(b["id"]) == str(booking_id):
            b["status"] = "cancelled"

    request.session["bookings"] = bookings
    request.session.modified = True

    return redirect("bookings:booking_list")
