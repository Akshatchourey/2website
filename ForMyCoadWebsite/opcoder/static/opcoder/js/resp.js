burger=document.querySelector('.burger')
navlist=document.querySelector('.uli1')
rightnav=document.querySelector('.div2')
navbar=document.querySelector('.nav-bar')

burger.addEventListener('click',()=>{
    rightnav.classList.toggle('v-class-resp')
    navlist.classList.toggle('v-class-resp')
    navbar.classList.toggle('h-nav-resp')
    burger.classList.toggle('burger')
})
