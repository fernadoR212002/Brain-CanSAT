// Opening the original file provides a player with a user gesture for audio.
if(location.protocol==='file:'||new URLSearchParams(location.search).has('play')){
 const player=document.querySelector('#play'), audio=document.querySelector('#score');
 player.hidden=false;
 function paint(){draw(audio.currentTime);if(!audio.paused&&!audio.ended)requestAnimationFrame(paint)}
 player.onclick=async()=>{if(!audio.paused){audio.pause();player.textContent='Continuar';return}
 if(audio.ended)audio.currentTime=0;await audio.play();player.textContent='Pausar';paint()};
 audio.onended=()=>{draw(15);player.textContent='Volver a reproducir'};
}
