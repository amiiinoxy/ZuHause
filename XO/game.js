
'use strict';
const LINES=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
const LEVELS={easy:{name:'Entspannt',hint:'Zufällige Züge. Einfach ausprobieren.'},normal:{name:'Clever',hint:'Taktisch – mit gelegentlichen Fehlern.'},hard:{name:'Perfekt',hint:'Spielt fehlerfrei. Ein Remis ist ein Erfolg.'}};
const KEY='spielraum-xo-v1';
const marks={X:'<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><path d="m15 15 34 34m0-34L15 49" stroke="currentColor" stroke-width="6" stroke-linecap="round"/></svg>',O:'<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><circle cx="32" cy="32" r="22" stroke="currentColor" stroke-width="6"/></svg>'};
function emptyStats(){return {easy:{wins:0,draws:0,losses:0},normal:{wins:0,draws:0,losses:0},hard:{wins:0,draws:0,losses:0}};}
function load(){let data;try{data=JSON.parse(localStorage.getItem(KEY));}catch{}const stats=emptyStats();for(const name of Object.keys(stats))for(const key of ['wins','draws','losses']){const n=data?.stats?.[name]?.[key];if(Number.isSafeInteger(n)&&n>=0)stats[name][key]=n;}return {level:LEVELS[data?.level]?data.level:'normal',human:['X','O'].includes(data?.human)?data.human:'X',stats};}
let saved=load(),level=saved.level,human=saved.human,stats=saved.stats;
let cells=Array(9).fill(null),turn='X',finished=false,round=0,timer=null,epoch=0;
let mode='computer',netEpoch=0,online=freshOnline(),peerLibraryPromise=null;
const board=document.getElementById('board'),status=document.getElementById('status'),tag=document.getElementById('turnTag');
const buttons=Array.from({length:9},(_,i)=>{const b=document.createElement('button');b.type='button';b.className='cell';b.dataset.index=i;b.addEventListener('click',()=>playHuman(i));b.addEventListener('keydown',event=>{const delta={ArrowRight:1,ArrowLeft:-1,ArrowDown:3,ArrowUp:-3}[event.key];if(delta===undefined)return;event.preventDefault();let j=i;for(let n=0;n<9;n++){j=(j+delta+9)%9;if(buttons[j].getAttribute('aria-disabled')==='false'){buttons[j].focus();break;}}});board.append(b);return b;});
function persist(){try{localStorage.setItem(KEY,JSON.stringify({level,human,stats}));}catch{document.getElementById('scoreHint').textContent='Statistik nur für diese Sitzung';}}
function outcome(b){for(const line of LINES)if(b[line[0]]&&line.every(i=>b[i]===b[line[0]]))return {winner:b[line[0]],line};return b.every(Boolean)?{winner:'draw',line:[]}:null;}
function minimax(b,player,ai,depth=0){const result=outcome(b);if(result)return result.winner==='draw'?0:result.winner===ai?10-depth:depth-10;const scores=[];for(let i=0;i<9;i++)if(!b[i]){b[i]=player;scores.push(minimax(b,player==='X'?'O':'X',ai,depth+1));b[i]=null;}return player===ai?Math.max(...scores):Math.min(...scores);}
function chooseMove(b,ai,difficulty,random=Math.random){const free=b.map((v,i)=>v===null?i:-1).filter(i=>i>=0);if(!free.length)return null;if(difficulty==='easy'||(difficulty==='normal'&&random()<.25))return free[Math.min(free.length-1,Math.floor(random()*free.length))];let best=-Infinity,moves=[];for(const i of free){b[i]=ai;const score=minimax(b,ai==='X'?'O':'X',ai);b[i]=null;if(score>best){best=score;moves=[i];}else if(score===best)moves.push(i);}return moves[Math.min(moves.length-1,Math.floor(random()*moves.length))];}

const $=id=>document.getElementById(id);
const opposite=symbol=>symbol==='X'?'O':'X';
function freshOnline(){
  return {role:null,phase:'idle',peer:null,conn:null,room:null,secret:null,invite:'',
    notice:'Erstelle eine Einladung für deinen Freund.',match:'',revision:0,hostSymbol:'X',
    scores:{host:0,guest:0,draws:0},requests:{host:false,guest:false},
    pending:false,handshaken:false,lastSeen:0,deadline:null,ackTimer:null,healthTimer:null,retryTimer:null};
}
function mySymbol(){return mode==='computer'?human:(online.role==='guest'?opposite(online.hostSymbol):online.hostSymbol);}
function connected(){return online.phase==='connected'&&Boolean(online.conn?.open);}
function playable(){return mode==='computer'||(connected()&&!online.pending);}
function scores(){
  let s=stats[level];
  if(mode==='friend')s={wins:online.scores[online.role||'host'],draws:online.scores.draws,losses:online.scores[online.role==='guest'?'host':'guest']};
  for(const key of ['wins','draws','losses'])$(key).textContent=s[key];
  $('scoreHint').textContent=mode==='friend'?'Gemeinsamer Spielstand · Dieser Raum':'Deine Statistik · '+LEVELS[level].name;
  $('lossesLabel').textContent=mode==='friend'?'Freundes-Siege':'Computer-Siege';
  $('resetStats').hidden=mode==='friend';
}
function updateOnlineUI(){
  $('onlineNotice').textContent=online.notice;
  $('createInvite').hidden=online.role!==null;
  $('inviteBox').hidden=!online.invite;
  $('inviteLink').value=online.invite;
  $('shareInvite').hidden=!navigator.share;
  $('retryConnect').hidden=!['error','interrupted'].includes(online.phase)||!online.role;
  $('retryConnect').textContent=online.role==='host'?'Neue Einladung erstellen':'Erneut verbinden';
  $('leaveRoom').hidden=!online.role;
  $('leaveRoom').textContent=online.role==='host'?'Raum schließen':'Spiel verlassen';
  const requested=online.requests[online.role||'host'];
  const otherRequested=online.requests[online.role==='guest'?'host':'guest'];
  $('newRound').disabled=!connected()||requested;
  $('newRound').textContent=requested?'Warte auf Zustimmung …':otherRequested?'Neuer Runde zustimmen':finished?'Revanche anbieten':'Neustart anfragen';
  if(!connected()){
    status.textContent=({idle:'Erstelle einen Einladungslink.',loading:'Einladung wird vorbereitet …',waiting:online.match?'Freund getrennt. Warte auf Rückkehr …':'Warte auf deinen Freund …',joining:'Verbinde euch …',error:'Verbindung nicht möglich.',interrupted:'Verbindung unterbrochen …'})[online.phase]||'Verbinde euch …';
  }else if(finished){
    const result=outcome(cells);
    status.textContent=result?.winner==='draw'?'Unentschieden. Gut gespielt!':result?.winner===mySymbol()?'Dein Sieg. Schön gespielt!':'Dein Freund gewinnt. Revanche?';
  }else status.textContent=online.pending?'Zug wird übertragen …':turn===mySymbol()?'Du bist dran. Dein nächster Zug?':'Dein Freund ist dran.';
}
function render(){
  if(mode==='friend')updateOnlineUI();
  document.body.dataset.live=String(mode==='friend'&&connected());
  const result=outcome(cells),symbol=mySymbol(),ready=playable();
  for(let i=0;i<9;i++){
    const b=buttons[i],mark=cells[i];
    b.innerHTML=mark?marks[mark]:'';b.dataset.value=mark||'';
    b.className='cell'+(result?.line.includes(i)?' winner':'')+' preview-'+symbol.toLowerCase();
    b.setAttribute('aria-disabled',String(!ready||finished||turn!==symbol||Boolean(mark)));
    b.setAttribute('aria-label',`Reihe ${Math.floor(i/3)+1}, Spalte ${i%3+1}: ${mark||'frei'}`);
  }
  $('humanPlayer').classList.toggle('active',ready&&!finished&&turn===symbol);
  $('aiPlayer').classList.toggle('active',ready&&!finished&&turn!==symbol);
  $('humanSymbol').textContent='Spielst mit '+symbol;
  $('aiSymbol').textContent='Spielt mit '+opposite(symbol);
  $('opponentName').textContent=mode==='friend'?'Freund':'Computer';
  $('roundLabel').textContent='RUNDE '+(round?String(round).padStart(2,'0'):'–');
  tag.dataset.state=finished?(result?.winner===symbol?'win':'done'):(ready&&turn===symbol?'play':'thinking');
  scores();
}
function complete(){
  const result=outcome(cells);if(!result)return false;
  finished=true;const key=result.winner==='draw'?'draws':result.winner===human?'wins':'losses';
  stats[level][key]++;
  status.textContent=result.winner==='draw'?'Unentschieden. Gut gespielt!':result.winner===human?'Dein Sieg. Schön gespielt!':'Der Computer gewinnt. Revanche?';
  scores();persist();render();return true;
}
function scheduleAI(){
  const token=epoch;status.textContent='Der Computer überlegt …';render();
  timer=setTimeout(()=>{
    timer=null;if(token!==epoch||mode!=='computer'||finished||turn===human)return;
    const ai=opposite(human),move=chooseMove(cells,ai,level);if(move===null)return;
    cells[move]=ai;if(!complete()){turn=human;status.textContent='Du bist dran. Dein nächster Zug?';render();}
  },480);
}
function playHuman(i){
  if(!Number.isInteger(i)||i<0||i>8||finished||!playable()||turn!==mySymbol()||cells[i])return;
  if(mode==='friend'){
    if(online.role==='host')applyOnlineMove(i,'host',online.match,online.revision);
    else{
      online.pending=true;
      send({type:'move',index:i,match:online.match,revision:online.revision});
      clearTimeout(online.ackTimer);const token=netEpoch;
      online.ackTimer=setTimeout(()=>{
        if(token!==netEpoch||!online.pending)return;
        online.phase='interrupted';online.notice='Noch keine Antwort. Wir warten auf deinen Freund. Falls nötig: erneut verbinden.';
        send({type:'sync'});render();
      },10000);render();
    }
    return;
  }
  cells[i]=human;if(complete())return;turn=opposite(human);scheduleAI();
}
function start(){
  if(mode==='friend'){requestRematch();return;}
  epoch++;clearTimeout(timer);timer=null;cells=Array(9).fill(null);turn='X';finished=false;round++;
  document.querySelectorAll('[data-level]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.level===level)));
  document.querySelectorAll('[data-symbol]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.symbol===human)));
  $('difficultyHint').textContent=LEVELS[level].hint;
  $('newRound').disabled=false;$('newRound').textContent='Neue Runde';
  scores();status.textContent='Du bist dran. Los geht’s!';render();if(human==='O')scheduleAI();
}

// The room owner validates every move. Guests receive complete, versioned snapshots.
function randomHex(){return Array.from(crypto.getRandomValues(new Uint8Array(16)),v=>v.toString(16).padStart(2,'0')).join('');}
function send(data){
  if(!online.conn?.open)return false;
  try{online.conn.send(data);return true;}catch{return false;}
}
function state(){
  return {type:'state',v:1,room:online.room,match:online.match,revision:online.revision,
    board:cells.slice(),hostSymbol:online.hostSymbol,round,scores:{...online.scores},requests:{...online.requests}};
}
function sendState(){send(state());}
function beginOnlineRound(){
  if(online.role!=='host'||!connected())return;
  if(online.match)online.hostSymbol=opposite(online.hostSymbol);
  online.match=randomHex();online.revision++;online.requests={host:false,guest:false};
  cells=Array(9).fill(null);turn='X';finished=false;round++;
  online.notice='Ihr seid verbunden. Viel Spaß! X beginnt; nach jeder Revanche tauscht ihr die Zeichen.';
  render();sendState();
}
function applyOnlineMove(index,actor,match,revision){
  if(online.role!=='host'||!connected())return;
  const symbol=actor==='host'?online.hostSymbol:opposite(online.hostSymbol);
  if(match!==online.match||revision!==online.revision||!Number.isInteger(index)||index<0||index>8||finished||cells[index]||turn!==symbol){sendState();return;}
  cells[index]=symbol;turn=opposite(symbol);online.revision++;
  const result=outcome(cells);
  if(result){finished=true;online.scores[result.winner==='draw'?'draws':result.winner===online.hostSymbol?'host':'guest']++;}
  render();sendState();
}
function requestRematch(){
  if(!connected()||online.requests[online.role])return;
  if(online.role==='guest'){send({type:'rematch',match:online.match});return;}
  online.requests.host=true;online.revision++;
  if(online.requests.guest)beginOnlineRound();else{online.notice='Du hast eine neue Runde angeboten. Dein Freund muss noch zustimmen.';render();sendState();}
}
function acceptState(data){
  const integer=n=>Number.isSafeInteger(n)&&n>=0;
  if(data.v!==1||data.room!==online.room||typeof data.match!=='string'||!/^[a-f0-9]{32}$/.test(data.match)||!integer(data.revision)||data.revision<online.revision||!integer(data.round)||data.round<1||!['X','O'].includes(data.hostSymbol)||!Array.isArray(data.board)||data.board.length!==9||!data.board.every(v=>v===null||v==='X'||v==='O')||!data.scores||!['host','guest','draws'].every(k=>integer(data.scores[k]))||!data.requests||!['host','guest'].every(k=>typeof data.requests[k]==='boolean'))return;
  const xs=data.board.filter(v=>v==='X').length,os=data.board.filter(v=>v==='O').length;
  if(xs<os||xs>os+1)return;
  clearTimeout(online.deadline);clearTimeout(online.ackTimer);
  online.phase='connected';online.handshaken=true;online.pending=false;
  online.match=data.match;online.revision=data.revision;online.hostSymbol=data.hostSymbol;
  online.scores={...data.scores};online.requests={...data.requests};
  cells=data.board.slice();turn=xs===os?'X':'O';finished=Boolean(outcome(cells));round=data.round;
  online.notice=online.requests.host?'Dein Freund bietet eine neue Runde an. Mit „Neuer Runde zustimmen“ startet ihr gemeinsam neu.':online.requests.guest?'Du hast eine neue Runde angeboten. Dein Freund muss noch zustimmen.':'Ihr seid verbunden. Viel Spaß! X beginnt; nach jeder Revanche tauscht ihr die Zeichen.';
  render();
}
function activity(){
  online.lastSeen=Date.now();
  if(online.handshaken&&online.phase==='interrupted'){
    online.phase='connected';online.notice='Ihr seid wieder verbunden.';
    if(online.role==='host')sendState();else send({type:'sync'});
    render();
  }
}
function healthCheck(token){
  clearInterval(online.healthTimer);online.lastSeen=Date.now();
  online.healthTimer=setInterval(()=>{
    if(token!==netEpoch||!online.conn?.open)return;
    if(online.handshaken&&Date.now()-online.lastSeen>22000){online.phase='interrupted';online.notice='Verbindung unterbrochen. Lasst beide Spielseiten geöffnet; wir warten auf die Rückkehr.';render();}
    send({type:'ping',revision:online.revision});
  },5000);
}
function handleMessage(data){
  if(!data||typeof data!=='object'||Array.isArray(data))return;
  activity();
  if(data.type==='ping'){
    if(online.role==='host'&&online.handshaken&&data.revision!==online.revision)sendState();
    send({type:'pong'});return;
  }
  if(data.type==='pong')return;
  if(data.type==='error'){
    online.phase='error';online.notice=data.reason==='full'?'In diesem Raum spielen bereits zwei Personen. Bitte deinen Freund um eine neue Einladung.':'Diese Einladung ist ungültig. Bitte deinen Freund um einen neuen Link.';render();return;
  }
  if(online.role==='guest'){
    if(data.type==='state')acceptState(data);
    return;
  }
  if(data.type==='hello'){
    if(data.v!==1||data.secret!==online.secret){send({type:'error',reason:'invalid'});online.conn?.close();return;}
    clearTimeout(online.deadline);online.phase='connected';online.handshaken=true;
    online.notice='Dein Freund ist da. Viel Spaß!';
    if(online.match){render();sendState();}else beginOnlineRound();
    return;
  }
  if(!online.handshaken)return;
  if(data.type==='move')applyOnlineMove(data.index,'guest',data.match,data.revision);
  else if(data.type==='sync')sendState();
  else if(data.type==='rematch'&&data.match===online.match){
    if(online.requests.guest){sendState();return;}
    online.requests.guest=true;online.revision++;
    if(online.requests.host)beginOnlineRound();
    else{online.notice='Dein Freund bietet eine neue Runde an. Mit „Neuer Runde zustimmen“ startet ihr gemeinsam neu.';render();sendState();}
  }
}

// PeerJS supplies signaling and WebRTC transport; no server credentials are embedded.
function loadPeerLibrary(){
  if(typeof window.Peer==='function')return Promise.resolve();
  if(peerLibraryPromise)return peerLibraryPromise;
  peerLibraryPromise=new Promise((resolve,reject)=>{
    const script=document.createElement('script');script.src='vendor/peerjs.min.js';
    script.onload=()=>typeof window.Peer==='function'?resolve():reject(new Error('library'));
    script.onerror=()=>{script.remove();reject(new Error('library'));};
    document.head.append(script);
  }).catch(error=>{peerLibraryPromise=null;throw error;});
  return peerLibraryPromise;
}
function clearNetworkTimers(){
  clearTimeout(online.deadline);clearTimeout(online.ackTimer);clearTimeout(online.retryTimer);clearInterval(online.healthTimer);
}
function shutdownOnline(removeLink=true){
  netEpoch++;clearNetworkTimers();const previous=online;online=freshOnline();
  try{previous.conn?.close();previous.peer?.destroy();}catch{}
  if(removeLink&&location.hash.startsWith('#spiel='))history.replaceState(null,'',location.pathname+location.search);
  $('copyStatus').textContent='';
}
function setMode(next){
  if(!['computer','friend'].includes(next)||next===mode)return;
  epoch++;clearTimeout(timer);timer=null;shutdownOnline();mode=next;
  document.body.dataset.mode=mode;
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  $('computerSettings').hidden=mode==='friend';$('friendPanel').hidden=mode!=='friend';
  $('modeCaption').textContent=mode==='friend'?'Ein Link. Zwei Spieler.':'Dein Tempo. Dein Spiel.';
  document.querySelector('.eyebrow').textContent=mode==='friend'?'Du und dein Freund':'Du gegen den Computer';
  cells=Array(9).fill(null);turn='X';finished=false;round=0;
  if(mode==='computer')start();else render();
}
function networkError(message){
  clearTimeout(online.deadline);online.phase='error';online.notice=message;online.pending=false;render();
}
function attachConnection(connection,token){
  online.conn=connection;
  online.deadline=setTimeout(()=>{
    if(token!==netEpoch||online.handshaken)return;
    networkError('Die Verbindung dauert zu lange. Prüft, ob die Gastgeberseite geöffnet ist. Versucht es erneut oder nutzt ein anderes Netz.');
    connection.close();
  },22000);
  connection.on('open',()=>{
    if(token!==netEpoch||online.conn!==connection){connection.close();return;}
    healthCheck(token);
    if(online.role==='guest')send({type:'hello',v:1,secret:online.secret});
  });
  connection.on('data',data=>{
    if(token===netEpoch&&online.conn===connection)handleMessage(data);
  });
  connection.on('close',()=>{
    if(token!==netEpoch||online.conn!==connection)return;
    clearNetworkTimers();online.conn=null;online.pending=false;online.handshaken=false;
    if(online.phase!=='error'){
      online.phase=online.role==='host'?'waiting':'error';
      online.notice=online.role==='host'?'Dein Freund hat die Verbindung verlassen. Halte diese Seite geöffnet; mit demselben Link kann er zurückkehren.':'Die Gastgeberseite ist nicht mehr erreichbar. Wenn sie noch geöffnet ist, verbinde dich erneut. Wurde sie geschlossen oder neu geladen, braucht ihr eine neue Einladung.';
    }
    render();
  });
  connection.on('error',()=>{
    if(token!==netEpoch||online.conn!==connection)return;
    networkError('Die Verbindung wurde unterbrochen. Versucht es erneut. Manchmal hilft ein anderes Netz.');connection.close();
  });
}
function rejectConnection(connection,reason){
  const reject=()=>{try{connection.send({type:'error',reason});}catch{}setTimeout(()=>connection.close(),200);};
  if(connection.open)reject();else connection.on('open',reject);
  setTimeout(()=>connection.close(),3000);
}
async function setupPeer(role,room=null,secret=null){
  const restoreLink=role==='guest'?`#spiel=${room}.${secret}`:'';
  if(mode!=='friend')setMode('friend');
  shutdownOnline(false);const token=netEpoch;
  epoch++;clearTimeout(timer);timer=null;cells=Array(9).fill(null);finished=false;turn='X';round=0;
  online.role=role;online.room=room||'xo-'+randomHex();online.secret=secret||randomHex();
  online.phase=role==='host'?'loading':'joining';
  online.notice=role==='host'?'Dein Einladungslink wird vorbereitet …':'Wir verbinden dich mit deinem Freund. Die Gastgeberseite muss geöffnet sein.';
  if(restoreLink)history.replaceState(null,'',location.pathname+location.search+restoreLink);
  render();
  online.deadline=setTimeout(()=>{
    if(token===netEpoch&&!online.handshaken&&online.phase!=='waiting')networkError('Der Verbindungsdienst antwortet gerade nicht. Versucht es erneut oder nutzt ein anderes Netz.');
  },22000);
  try{
    await loadPeerLibrary();if(token!==netEpoch)return;
    const id=role==='host'?online.room:'xo-'+randomHex();
    const peer=new Peer(id,{host:'0.peerjs.com',port:443,path:'/',secure:true,debug:0});
    online.peer=peer;
    peer.on('open',()=>{
      if(token!==netEpoch)return;
      clearTimeout(online.deadline);
      if(role==='host'){
        if(!online.conn?.open)online.phase='waiting';
        const url=new URL(location.href);url.hash=`spiel=${online.room}.${online.secret}`;online.invite=url.href;
        online.notice=online.match?'Der Raum ist wieder erreichbar. Dein Freund kann denselben Einladungslink öffnen.':'Dein Link ist bereit. Schicke ihn deinem Freund und lass diese Seite geöffnet.';
        render();
      }else if(!online.conn){
        const connection=peer.connect(online.room,{reliable:true,serialization:'json',metadata:{game:'spielraum-xo',v:1,secret:online.secret}});
        attachConnection(connection,token);
      }
    });
    peer.on('connection',connection=>{
      if(token!==netEpoch||role!=='host'){connection.close();return;}
      const meta=connection.metadata;
      if(meta?.game!=='spielraum-xo'||meta?.v!==1||meta?.secret!==online.secret){rejectConnection(connection,'invalid');return;}
      if(online.conn){rejectConnection(connection,'full');return;}
      online.phase='joining';online.handshaken=false;online.notice='Dein Freund kommt ins Spiel …';
      attachConnection(connection,token);render();
    });
    peer.on('error',error=>{
      if(token!==netEpoch||online.conn?.open&&online.handshaken)return;
      networkError(error.type==='peer-unavailable'?'Diese Einladung ist gerade nicht erreichbar. Die Gastgeberseite muss geöffnet bleiben. Nach dem Schließen oder Neuladen braucht ihr eine neue Einladung.':'Der Verbindungsdienst ist nicht erreichbar. Versucht es erneut. Falls nötig: ein anderes Netz verwenden.');
    });
    peer.on('disconnected',()=>{
      if(token!==netEpoch||peer.destroyed)return;
      clearTimeout(online.retryTimer);
      online.retryTimer=setTimeout(()=>{
        if(token===netEpoch&&peer.disconnected&&!peer.destroyed){try{peer.reconnect();}catch{}}
      },1500);
    });
  }catch{
    if(token===netEpoch)networkError('Der Freundesmodus konnte nicht geladen werden. Lade die Seite neu und verwende einen aktuellen Browser.');
  }
}
function invitationFromHash(){
  const match=location.hash.match(/^#spiel=(xo-[a-f0-9]{32})\.([a-f0-9]{32})$/);
  return match?{room:match[1],secret:match[2]}:null;
}
async function copyInvite(){
  if(!online.invite)return;
  try{await navigator.clipboard.writeText(online.invite);$('copyStatus').textContent='Link kopiert. Jetzt an deinen Freund schicken.';}
  catch{
    $('inviteLink').focus();$('inviteLink').select();
    let copied=false;try{copied=document.execCommand('copy');}catch{}
    $('copyStatus').textContent=copied?'Link kopiert. Jetzt an deinen Freund schicken.':'Link markiert. Kopiere ihn über das Menü deines Browsers.';
  }
}
document.querySelectorAll('[data-level]').forEach(b=>b.addEventListener('click',()=>{
  if(mode!=='computer'||level===b.dataset.level)return;level=b.dataset.level;persist();start();
}));
document.querySelectorAll('[data-symbol]').forEach(b=>b.addEventListener('click',()=>{
  if(mode!=='computer'||human===b.dataset.symbol)return;human=b.dataset.symbol;persist();start();
}));
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
$('newRound').addEventListener('click',start);
$('resetStats').addEventListener('click',()=>{if(mode!=='computer')return;stats[level]={wins:0,draws:0,losses:0};scores();persist();});
$('createInvite').addEventListener('click',()=>setupPeer('host'));
$('copyInvite').addEventListener('click',copyInvite);
$('shareInvite').addEventListener('click',async()=>{
  if(!online.invite)return;
  try{await navigator.share({title:'Eine Runde X O?',text:'Spiel mit mir! Ich warte auf dich.',url:online.invite});}
  catch(error){if(error.name!=='AbortError')copyInvite();}
});
$('retryConnect').addEventListener('click',()=>online.role==='host'?setupPeer('host'):setupPeer('guest',online.room,online.secret));
$('leaveRoom').addEventListener('click',()=>{shutdownOnline();cells=Array(9).fill(null);round=0;turn='X';finished=false;render();});
window.addEventListener('hashchange',()=>{
  const invite=invitationFromHash();
  if(invite&&!(mode==='friend'&&online.room===invite.room&&online.secret===invite.secret))setupPeer('guest',invite.room,invite.secret);
});
start();
const invite=invitationFromHash();
if(invite)setupPeer('guest',invite.room,invite.secret);
else if(location.hash.startsWith('#spiel=')){
  setMode('friend');online.phase='error';online.notice='Dieser Einladungslink ist unvollständig oder ungültig. Bitte deinen Freund um einen neuen Link.';render();
}
