(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-59394184-1', 'auto');
ga('set', 'dimension1', 'TST');
ga('set', 'dimension2', 'Test system (1745)');
ga('send', 'pageview');


window.onerror = function (message, file, line, col, error) {
    ga('send', 'event', 'JS Error', message, navigator.userAgent + ' -> ' + file + " : " + line + " : " + col, { nonInteraction: true });
};
window.addEventListener("error", function (e) {
    ga('send', 'event', 'JS Error', e.error.message, navigator.userAgent + ' -> ' + e.error.stack, { nonInteraction: true });
});