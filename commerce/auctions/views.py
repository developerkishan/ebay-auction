from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , get_object_or_404 , redirect
from django.urls import reverse
from auctions.models import Listing , Bid , User , Comment,Watchlist,Category
from auctions.forms import ListingForm, BidForm , CommentForm
from django.contrib import messages

def index(request):
    listings = Listing.objects.filter(is_active = True)
    return render(request, "auctions/index.html",{"listings": listings})

def categories_view(request):
    
    categories = Listing.objects.values_list('category__name',flat=True).distinct()
    return render(request, "auctions/categories.html",{
        "categories": categories
    })
def category_listings(request,category_name):
    category = get_object_or_404(Category, name=category_name)
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category_listing.html",{
        "listings": listings
    })

def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.current_price = listing.starting_bid
            listing.creator = request.user
            listing.save()
            return redirect('listing_detail',listing_id = listing.id)
        else:
            return render(request, "auctions/create_listing.html" , {"form":form})
    else:
        form = ListingForm()
        return render(request, "auctions/create_listing.html" , {"form":form})

def listing_detail(request,listing_id):
    listing = get_object_or_404(Listing,id = listing_id)
    bids = Bid.objects.filter(listing=listing)
    comments = Comment.objects.filter(listing=listing)
    in_watchlist = False
    bidform = BidForm()
    commentform = CommentForm()
    if request.user.is_authenticated:
        in_watchlist= Watchlist.objects.filter(user=request.user,listing=listing).exists()
    return render(request,"auctions/listing_detail.html",{
        "listing":listing,
        "bids": bids,
        "comments": comments,
        "in_watchlist": in_watchlist,
        "bidform": bidform,
        "commentform": commentform})

def close_auction(request,listing_id):
    listing = get_object_or_404(Listing,id = listing_id)
    if request.user == listing.creator:
        listing.is_active = False
        listing.save()

        highest_bid = Bid.objects.filter(listing=listing).order_by('-bid_amount').first()
        if highest_bid:
            winner = highest_bid.bidder
            messages.success(request,f"Auction for {listing.title} has been closed. The winner is {winner.username} ")
        else:
            winner = None
            messages.info(request,f"Auction for {listing.title} has been closed. There were no bids .")    
        return redirect('listing_detail',listing_id = listing.id)
    else:
        messages.error(request,"You are not authorized to close this aution. ")
        return redirect('listing_detail', listing_id = listing_id)
    

def add_comment(request, listing_id):
    listing = get_object_or_404(Listing,id = listing_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.commenter = request.user
            comment.save()
            return redirect('listing_detail',listing_id = listing.id)
        else:
            messages.error("The data is not valid")
            return redirect('listing_detail',listing_id = listing.id)
    return redirect('listing_detail',listing_id = listing.id)

def add_to_watchlist(request,listing_id):
    listing = get_object_or_404(Listing,id=listing_id)
    watchlist = Watchlist(listing = listing , user = request.user)
    watchlist.save()
    return redirect('listing_detail',listing_id = listing.id)

def remove_from_watchlist(request,listing_id):
    listing = get_object_or_404(Listing,id=listing_id)
    watchlist = Watchlist.objects.filter(listing = listing.id)
    watchlist.delete()
    return redirect('listing_detail',listing_id = listing.id)

def watchlist_view(request):
    user_watchlists = Watchlist.objects.filter(user=request.user)
    listings = [user_watchlist.listing for user_watchlist in user_watchlists ]

    return render(request,'auctions/watchlist.html',{
        'listings': listings
    })



def place_bid(request,listing_id):
    listing = get_object_or_404(Listing,id = listing_id)
    if request.method == 'POST':
        bidform = BidForm(request.POST)
        if request.user.is_authenticated:
            if bidform.is_valid():
                bid_amount = bidform.cleaned_data['bid_amount']
                if bid_amount >= listing.starting_bid and bid_amount > listing.current_price:
                    bid = Bid(
                        listing = listing,
                        bidder = request.user,
                        bid_amount = bid_amount
                    )
                    bid.save()
                    listing.current_price = bid.bid_amount
                    listing.save()
                    messages.success(request, 'Your bid has been placed successfully.')
                    return redirect('listing_detail',listing_id = listing.id)
                else:
                    messages.error(request, 'Your bid must be greater than the starting bid and the current price.')
            else:
                messages.error(request, 'Invalid bid amount.')
        else:
            return redirect("login")
    return  redirect('listing_detail', listing_id=listing.id)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
