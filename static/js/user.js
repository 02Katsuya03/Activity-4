/*===== EXPANDER MENU  =====*/ 
const showMenu = (toggleId, navId)=>{
    const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId)
  
    if(toggle && nav){
      toggle.addEventListener('click', ()=>{
        nav.classList.toggle('show')
        toggle.classList.toggle('bx-x')
      })
    }
  }
  showMenu('header-toggle','nav-menu')

  /*===== ACTIVE AND REMOVE MENU =====*/
const navLink = document.querySelectorAll('.nav__link');   

function linkAction(){
  /*Active link*/
  navLink.forEach(n => n.classList.remove('active'));
  this.classList.add('active');
}
navLink.forEach(n => n.addEventListener('click', linkAction));

// JavaScript to enable the automated carousel sliding
$(document).ready(function () {
  $('#carouselExample').carousel({
      interval: 3000 // Auto slide every 3 seconds
  });
});

document.addEventListener("DOMContentLoaded", function() {
  const photoInput = document.querySelector('input[name="photo"]');
  const previewImage = document.getElementById("photo-preview");
  const previewText = document.getElementById("preview-text");

  photoInput.addEventListener("change", function(event) {
      const file = event.target.files[0];
      if (file) {
          const reader = new FileReader();
          reader.onload = function(e) {
              previewImage.src = e.target.result;
              previewImage.style.display = "block";
              previewText.style.display = "none";
          };
          reader.readAsDataURL(file);
      } else {
          previewImage.src = "#";
          previewImage.style.display = "none";
          previewText.style.display = "block";
      }
  });
});

document.addEventListener("DOMContentLoaded", function() {
  flatpickr("#datePicker", {
      dateFormat: "d M Y",  // Custom date format (Day Month Year)
      locale: "en",  // Use "en" for English
  });
});

let sidebar = document.querySelector(".sidebar");
let closeBtn = document.querySelector("#btn");
let searchBtn = document.querySelector(".bx-search");
closeBtn.addEventListener("click", ()=>{
sidebar.classList.toggle("open");
menuBtnChange();//calling the function(optional)
});
searchBtn.addEventListener("click", ()=>{ // Sidebar open when you click on the search iocn
sidebar.classList.toggle("open");
menuBtnChange(); //calling the function(optional)
});
// following are the code to change sidebar button(optional)
function menuBtnChange() {
if(sidebar.classList.contains("open")){
 closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");//replacing the iocns class
}else {
 closeBtn.classList.replace("bx-menu-alt-right","bx-menu");//replacing the iocns class
}
}

document.addEventListener("DOMContentLoaded", function () {
const recentItems = document.getElementById("recent-items");

let isDragging = false;
let startX, startY, initialX, initialY;

recentItems.addEventListener("mousedown", (e) => {
  isDragging = true;
  startX = e.clientX;
  startY = e.clientY;
  const rect = recentItems.getBoundingClientRect();
  initialX = rect.left;
  initialY = rect.top;

  document.body.style.userSelect = "none"; // Disable text selection
});

document.addEventListener("mousemove", (e) => {
  if (!isDragging) return;
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  recentItems.style.left = `${initialX + dx}px`;
  recentItems.style.top = `${initialY + dy}px`;
});

document.addEventListener("mouseup", () => {
  isDragging = false;
  document.body.style.userSelect = ""; // Re-enable text selection
});
});

