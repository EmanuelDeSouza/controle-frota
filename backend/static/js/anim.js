document.querySelectorAll("#truckList li").forEach((li, i) => {
  li.style.animationDelay = `${i * 0.1}s`;
});