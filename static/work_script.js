var $messages = $(".messages-content"),
  d,
  h,
  m,
  i = 0;

$(window).load(function () {
  $messages.mCustomScrollbar();
  setTimeout(function () {
    fakeMessage();
  }, 100);
});

function updateScrollbar() {
  $messages.mCustomScrollbar("update").mCustomScrollbar("scrollTo", "bottom", {
    scrollInertia: 10,
    timeout: 0
  });
}

function setDate() {
  d = new Date();
  if (m != d.getMinutes()) {
    m = d.getMinutes();
    $('<div class="timestamp">' + d.getHours() + ":" + m + "</div>").appendTo(
      $(".message:last")
    );
  }
}

function insertMessage() {
  msg = $(".message-input").val();
  if ($.trim(msg) == "") {
    return false;
  }
  $('<div class="message message-personal">' + msg + "</div>")
    .appendTo($(".mCSB_container"))
    .addClass("new");
  setDate();
  $(".message-input").val(null);
  updateScrollbar();
  setTimeout(function () {
    fakeMessage();
  }, 1000 + Math.random() * 20 * 100);
}

$(".message-submit").click(function () {
  insertMessage();
});

$(window).on("keydown", function (e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
});

var Fake = [
  "Hey,How are you? What do you prefer?<a href='/hotels'><button style='margin:5px'>Hotels</button></a><a href='/restaurants'><button style='margin:5px'>Restaurants</button></a><a href='/events'><button style='margin:5px'>Events</button></a><a href='/tourists'><button style='margin:5px'>Tourists</button></a><a href='/hospitals'><button style='margin:5px'>Hospitals</button></a><a href='/police-stations'><button style='margin:5px'>Police Station</button></a><a href='/banks'><button style='margin:5px'>Banks</button></a><a href='/railway-stations'><button style='margin:5px'>Railway Stations</button></a><a href='/gas-stations'><button style='margin:5px'>Gas Stations</button></a><a href='/doctors'><button style='margin:5px'>Doctors</button></a>",
  "Hope you are doing fine",
  "I think you're a nice person",
  "Why do you think that?",
  "Can you explain?",
  "Anyway I've gotta go now",
  "It was a pleasure chat with you",
  "Time to make a new codepen",
  "Bye",
  ":)"
];

function fakeMessage() {
  if ($(".message-input").val() != "") {
    return false;
  }
  $(
    '<div class="message loading new"><figure class="avatar"><img src="https://w7.pngwing.com/pngs/704/214/png-transparent-flight-aviation-travel-chatbot-internet-bot-flight-company-logo-grass.png" /></figure><span></span></div>'
  ).appendTo($(".mCSB_container"));
  updateScrollbar();

  setTimeout(function () {
    $(".message.loading").remove();
    $(
      '<div class="message new"><figure class="avatar"><img src="https://w7.pngwing.com/pngs/704/214/png-transparent-flight-aviation-travel-chatbot-internet-bot-flight-company-logo-grass.png" /></figure>' +
        Fake[i] +
        "</div>"
    )
      .appendTo($(".mCSB_container"))
      .addClass("new");
    setDate();
    updateScrollbar();
    i++;
  }, 1000 + Math.random() * 20 * 100);
}