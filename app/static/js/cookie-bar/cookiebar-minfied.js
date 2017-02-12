function setupCookieBar(){function e(){console.log("cookieBAR - Timeout for ip geolocation"),L.abort(),T=!0}function t(){var e=n(),t="";u("theme")&&(t="-"+u("theme"));var o=h.replace(/[^\/]*$/,""),i=h.indexOf(".min")>-1?".min":"",a=document.createElement("link");a.setAttribute("rel","stylesheet"),a.setAttribute("href",o+"cookiebar"+t+i+".css"),document.head.appendChild(a);var c=new XMLHttpRequest;c.open("GET",o+"/lang/"+e+".html",!0),c.onreadystatechange=function(){if(4===c.readyState&&200===c.status){var e=document.createElement("div");if(e.innerHTML=c.responseText,document.getElementsByTagName("body")[0].appendChild(e),g=document.getElementById("cookie-bar"),y=document.getElementById("cookie-bar-button"),k=document.getElementById("cookie-bar-button-no"),b=document.getElementById("cookie-bar-prompt"),f=document.getElementById("cookie-bar-prompt-button"),v=document.getElementById("cookie-bar-prompt-close"),E=document.getElementById("cookie-bar-prompt-content"),B=document.getElementById("cookie-bar-no-consent"),thirdparty=document.getElementById("cookie-bar-thirdparty"),tracking=document.getElementById("cookie-bar-tracking"),scrolling=document.getElementById("cookie-bar-scrolling"),privacyPage=document.getElementById("cookie-bar-privacy-page"),privacyLink=document.getElementById("cookie-bar-privacy-link"),u("showNoConsent")||(B.style.display="none",k.style.display="none"),u("blocking")&&(l(b,500),v.style.display="none"),u("thirdparty")&&(thirdparty.style.display="block"),u("tracking")&&(tracking.style.display="block"),u("scrolling")&&(scrolling.style.display="inline-block"),u("top")?(g.style.top=0,s("top")):(g.style.bottom=0,s("bottom")),u("privacyPage")){var t=decodeURIComponent(u("privacyPage"));privacyLink.href=t,privacyPage.style.display="inline-block"}p(),l(g,250),s()}},c.send()}function o(){var e=document.getElementsByTagName("script");for(i=0;i<e.length;i+=1)if(e[i].hasAttribute("src")&&(path=e[i].src,path.indexOf("cookiebar")>-1))return path}function n(){var e=u("forceLang");return e===!1&&(e=navigator.language||navigator.userLanguage),e=e.substr(0,2),CookieLanguages.indexOf(e)<0&&(e="en"),e}function a(){var e=document.cookie.match(/(;)?cookiebar=([^;]*);?/);return null==e?void 0:decodeURI(e[2])}function c(e,t){var o=30;u("remember")&&(o=u("remember"));var n=new Date;n.setDate(n.getDate()+parseInt(o));var i=encodeURI(t)+(null===o?"":"; expires="+n.toUTCString()+";path=/");document.cookie=e+"="+i}function r(){document.cookie.split(";").forEach(function(e){document.cookie=e.replace(/^\ +/,"").replace(/\=.*/,"=;expires="+(new Date).toUTCString()+";path=/")}),localStorage.clear()}function l(e,t){var o=e.style;o.opacity=0,o.display="block",function n(){(o.opacity-=-.1)>.9?null:setTimeout(n,t/10)}()}function d(e,t){var o=e.style;o.opacity=1,function n(){(o.opacity-=.1)<.1?o.display="none":setTimeout(n,t/10)}()}function s(e){setTimeout(function(){var t=document.getElementById("cookie-bar").clientHeight,o=document.getElementsByTagName("body")[0],n=o.currentStyle||window.getComputedStyle(o);switch(e){case"top":o.style.marginTop=parseInt(n.marginTop)+t+"px";break;case"bottom":o.style.marginBottom=parseInt(n.marginBottom)+t+"px"}},300)}function m(){var e=document.getElementById("cookie-bar").clientHeight;if(u("top")){var t=parseInt(document.getElementsByTagName("body")[0].style.marginTop);document.getElementsByTagName("body")[0].style.marginTop=t-e+"px"}else{var o=parseInt(document.getElementsByTagName("body")[0].style.marginBottom);document.getElementsByTagName("body")[0].style.marginBottom=o-e+"px"}}function u(e){var t=h.split(e+"=");return t[1]?t[1].split(/[&?]+/)[0]:!1}function p(){if(y.addEventListener("click",function(){c("cookiebar","CookieAllowed"),m(),d(b,250),d(g,250)}),k.addEventListener("click",function(){var e=B.textContent.trim(),t=window.confirm(e);t===!0&&(r(),c("cookiebar","CookieDisallowed"),m(),d(b,250),d(g,250))}),f.addEventListener("click",function(){l(b,250)}),v.addEventListener("click",function(){d(b,250)}),u("scrolling")){var e=document.body.getBoundingClientRect().top,t=!1;window.addEventListener("scroll",function(){t===!1&&(document.body.getBoundingClientRect().top-e>250||document.body.getBoundingClientRect().top-e<-250)&&(c("cookiebar","CookieAllowed"),m(),d(b,250),d(g,250),t=!0)})}}var g,y,k,b,f,v,E,B,h=o(),T=!1,I=!1;"CookieDisallowed"==a()&&(r(),c("cookiebar","CookieDisallowed"));var L=new XMLHttpRequest;L.open("GET","//freegeoip.io/json/",!0),L.onreadystatechange=function(){if(4===L.readyState&&200===L.status){clearTimeout(C);var e=JSON.parse(L.responseText).country_code;cookieLawStates.indexOf(e)>-1?T=!0:I=!0}};var C=setTimeout(e,1500);if(L.send(),document.cookie.length>0||window.localStorage.length>0){var w=a();void 0===w?T=!0:I=!0}u("always")&&(T=!0),T===!0&&I===!1&&t()}var CookieLanguages=["ca","da","de","en","es","fr","hu","it","nl","pt","ro","si"],cookieLawStates=["BE","BG","CZ","DK","DE","EE","IE","EL","ES","FR","IT","CY","LV","LT","LU","HU","MT","NL","AT","PL","PT","RO","SI","SK","FI","SE","GB"];document.addEventListener("DOMContentLoaded",function(){setupCookieBar()});