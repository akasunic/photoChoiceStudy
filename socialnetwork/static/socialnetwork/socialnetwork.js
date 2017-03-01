// wait until doc is loaded first
$(document).ready(function(){
    $('#stream').find('.orig_msg').append(addComment());
    window.onload = getComments;
    $('#id_text').keypress(function() { //for checking length of post input
        var numChars = $(this).val().length;
        $('#post_len').html('You used ' + numChars + ' of 160 characters');
    })
    $('body').find('.commentText').keypress(function() { //for checking length of post input
        var numChars = $(this).val().length;
        var p = $(this).prev('p'); //display counter right above
        p.html('You used ' + numChars + ' of 160 characters');
    })
    var page = String(window.location.href);
    window.setInterval(getComments, 5000);
    if (page.indexOf("followfeed")>=0){ //find if on followfeed page
        //causes a subset of posts (those of people following) to be re-fetched every 5 secs
        window.setInterval(getFeed, 5000);
    }

    else if(page.indexOf("globalstream")>=0){ //find if on globalstream
        // causes all posts to be re-fetched every 5 seconds
        window.setInterval(getStream, 5000);
    }
    else{}//don't load if on neither of these pages (though shouldn't happen)
    
});

//security!
function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

//adds comment boxes (input area, button) to each post/message
//each button has a click function that will send an ajax post request to send new comment to server
function addComment(){
    var tr= $('<div>').addClass("commentBox");
    var p = $('<p>');
    var comment = $('<textarea>').addClass("commentText").attr('maxlength', 160);
    var btn = $('<button>').text("comment");
    btn.on('click', function(){
        var comm = $(this).prev('textarea').val();
        var postId = $(this).closest('td').attr('id');
        var token = getCSRFToken();
        $(this).prev('textarea').val('');//empty the textarea box after we've gotten the info from it
        $.ajax({
            url: "/socialnetwork/add_comment",
            type: "POST", 
            data: {
                'csrfmiddlewaretoken': token,
                'comm': comm, 
                'postId': postId
            },
            dataType: "json",
            success: function(response){
                if (Array.isArray(response)){
                    updateComments(response);
                }
                else{
                    displayError(response.error);
                }
            }
        })
    });

    tr.append(p);
    tr.append(comment);
    tr.append(btn);
    return tr;
}

function displayError(message) {
    $("#error").html(message);
}
// used for the global stream page
function getStream() {
    $.ajax({
        url: "/socialnetwork/get_posts",
        dataType : "json",
        success: updatePosts
    });
}

// used for the followfeed page (sends back a subset of messages)
function getFeed() {
    $.ajax({
        url: "/socialnetwork/get_feed",
        dataType : "json",
        success: updatePosts
    });
}

//used for both globalstream and followfeed
function getComments(){
    $.ajax({
        url: "/socialnetwork/get_comments",
        dataType:"json",
        success: updateComments
    })
}

//used for both globalstream and followfeed
function updateComments(comments){
    $('.comment').remove(); //remove all existing comments
    $(comments).each(function(){
        msg_id = this['msg_id'];
        if ($('#' + msg_id).length>0){ //do not append comment if the message not displayed (for follow feed)
            user = this['commenter_id'];
            var time = new Date(this.time);
            var photo;
            if (this['photo']){
                photo = '<a href ="/socialnetwork/profile/' + user + '"><img src="/socialnetwork/streamphoto/' + user + '"  alt="profile photo" width="40px"></a>';
            }
            else {photo = '';}
            time = time.toLocaleString();
            $('#' + msg_id).append('<div class="comment" style = "padding-left:40px;">' + 
                photo +
                '<span style="padding-left:5px;">' + this.user + 
                ', ' + time + '</span>' + 
                '<br>' +
                '<span style="padding-left:30px;">'+ this.comm + '</span>' +
                '<br><br>' +
                '</div>');
        }
    });

}

//for both globalstream and followfeed pages (directed from different functions in views.py)
function updatePosts(msgs) {
    var stream = $("#stream");
    $(msgs).each(function() {
        var time = new Date(this.messageTime);
        time = time.toLocaleString();
        var tr = $('<tr>');
        var photoString = '<td id="' + this['id'] + '"><a href ="/socialnetwork/profile/' + this['id'] + '"><img src="/socialnetwork/streamphoto/' + this['id'] + '"  alt="profile photo" width="50px"></a>';
        var restString = '<br>' + time + ', <a href="profile/' + this['id'] + '">' + this.user + ':</a><br><div class="msg">' + this['text'] + '</div>';
        var div = addComment();
        if (this['photo']){
            tr.html($(photoString + restString).append(div).append($('</td>')));   
        }
        else{
            tr.html($('<td id="' + this['id'] + '">' + restString).append(div).append($('</td>')));
        }
        tr.prependTo(stream);  
    });
}


