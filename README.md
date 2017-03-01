HW6

-----------------------
Notes still relevant from HW5:
-----------------------
I used Python 2.7

I used Twitter Bootstrap + custom CSS, like I did for HW4 and HW5. I continued making updates to the style. 

I saved all my image files to the images folder; in my gitignore, I ignored this entire directory (eg images)

For photos, I didn't make this a required field. So I just don't show photos (on the stream and on the individual profile pages) if photos are not available.

I am sure I forgot some issues with security, but I tried :(

Because users are not supposed to follow themselves, and because I have their newsfeed as the default view when they log in (rather than the global stream), I added a feature to allow them to see their latest post so they will know they successfully posted. 

--------------------------------
New notes for HW6
-----------------------------
I used jQuery for this assignment to implement ajax. In my ajax functionality, I updated only posts not already on the page, whereas for comments, I would refresh all the comments each time.

I incorporated feedback from HW4. For example, I added counters for the comments and posts,  I now have a consistent header, and the ability for users to go directly to their own profiles.

I fixed some issues that I thought I had fixed in HW5 with the photo displays, etc.

Instead of serializers.serialize, I used json.

I was also trying to fix up the form validation and was able to make some improvements; I am still having issues with this. At least for the cases I've thought of, my app will not 'break' on invalid inputs, etc. However, the errors do not always display because of the way I'm rendering my responses.

Per usual, I referred quite a bit to class examples, Django documentation, and Stack Overflow.

Thank you for your time and feedback.