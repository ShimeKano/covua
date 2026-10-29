(() => {
'use strict';
const ASSET='./assneo/';
const files={k:'wk.png',q:'wq.png',r:'wr.png',b:'wb.png',n:'wn.png',p:'wp.png',K:'bk.png',Q:'bq.png',R:'br.png',B:'bb.png',N:'bn.png',P:'bp.png'};
const game=new Chess();
let flipped=false,selected=null,legal=[],initialMinutes=5,remaining={w:300000,b:300000},active='w',lastMove=null,timer=null,started=false,finished=false,history=[],reviewWorker=null,reviewRunning=false;
const $=id=>document.getElementById(id);const board=$('board');
function format(ms){ms=Math.max(0,ms);const sec=Math.ceil(ms/1000);return String(Math.floor(sec/60)).padStart(2,'0')+':'+String(sec%60).padStart(2,'0')}
function renderClocks(){$('whiteClock').querySelector('strong').textContent=format(remaining.w);$('blackClock').querySelector('strong').textContent=format(remaining.b);$('whiteClock').classList.toggle('active',active==='w'&&started&&!finished);$('blackClock').classList.toggle('active',active==='b'&&started&&!finished);$('whiteStatus').textContent='Trắng'+(active==='w'&&started&&!finished?' · Đang chạy':'');$('blackStatus').textContent='Đen'+(active==='b'&&started&&!finished?' · Đang chạy':'')}
function squareName(r,c){return 'abcdefgh'[c]+(8-r)}
function render(){board.innerHTML='';const matrix=game.board();for(let vr=0;vr<8;vr++)for(let vc=0;vc<8;vc++){const r=flipped?7-vr:vr,c=flipped?7-vc:vc,sq=squareName(r,c),piece=matrix[r][c],el=document.createElement('button');el.type='button';el.className='square '+(((r+c)%2===0)?'light':'dark');el.dataset.square=sq;el.setAttribute('aria-label',sq);if(selected===sq)el.classList.add('selected');if(lastMove&&(lastMove.from===sq||lastMove.to===sq))el.classList.add('last');if(legal.includes(sq)){el.classList.add('target');if(piece)el.classList.add('occupied')}if(vc===0){const coord=document.createElement('span');coord.className='coord';coord.textContent=String(8-r);el.append(coord)}if(vr===7){const coord=document.createElement('span');coord.className='coord';coord.style.left='auto';coord.style.right='4px';coord.style.top='auto';coord.style.bottom='1px';coord.textContent='abcdefgh'[c];el.append(coord)}if(piece){const img=document.createElement('img');img.draggable=false;img.alt='';img.src=ASSET+files[piece.color==='w'?piece.type:piece.type.toUpperCase()];img.onerror=()=>{if(window.COVUA_DIAGNOSTICS)window.COVUA_DIAGNOSTICS.report('PIECE_IMAGE_ERROR','Không tải được ảnh quân cờ: '+img.src)};el.append(img)}el.addEventListener('click',()=>clickSquare(sq));board.append(el)}renderMoves();renderStatus();renderClocks()}
function clickSquare(sq){if(finished)return;if(window.COVUA_ONLINE?.isOnline()&&!window.COVUA_ONLINE.canMove(game.turn()))return;const p=game.get(sq);if(selected&&legal.includes(sq)){const beforeFen=game.fen(),mover=game.turn(),move=game.move({from:selected,to:sq,promotion:'q'});if(move){history.push({move:{...move},beforeFen,afterFen:game.fen(),mover});lastMove=move;selected=null;legal=[];afterMove();return}}if(p&&p.color===game.turn()){selected=sq;legal=game.moves({square:sq,verbose:true}).map(m=>m.to)}else{selected=null;legal=[]}render()}
function renderMoves(){const list=$('moves');$('move-count').textContent=history.length+' nước';if(!history.length){list.innerHTML='<p class="muted">Nước đi sẽ hiện ở đây.</p>';return}let html='<table><thead><tr><th>#</th><th>Trắng</th><th>Đen</th></tr></thead><tbody>';for(let i=0;i<history.length;i+=2)html+='<tr><td>'+(Math.floor(i/2)+1)+'.</td><td>'+(history[i]?.move.san||'')+'</td><td>'+(history[i+1]?.move.san||'')+'</td></tr>';html+='</tbody></table>';list.innerHTML=html;list.scrollTop=list.scrollHeight}
function renderStatus(){let s;if(finished)s='Ván cờ đã kết thúc';else if(game.in_checkmate())s='Chiếu bí!';else if(game.in_draw())s='Ván hòa';else s=(game.turn()==='w'?'Trắng':'Đen')+' đi'+(game.in_check()?' · đang bị chiếu':'');$('status').textContent=s}
function stopClock(){if(timer){clearInterval(timer);timer=null}}
function startClock(){stopClock();if(!started||finished)return;let prev=Date.now();timer=setInterval(()=>{const now=Date.now();remaining[active]-=now-prev;prev=now;if(remaining[active]<=0){remaining[active]=0;finished=true;stopClock();$('status').textContent='Hết giờ — '+(active==='w'?'Đen':'Trắng')+' thắng';render();showReviewButton()}else renderClocks()},100)}
function showReviewButton(){const b=$('review');if(b)b.hidden=!(finished&&history.length>0)}
function afterMove(){started=true;active=game.turn();if(game.game_over()){finished=true;stopClock();showReviewButton()}else startClock();render();if(window.COVUA_ONLINE?.isOnline())window.COVUA_ONLINE.publishPosition()}
function newGame(){if(window.COVUA_ONLINE?.isOnline())return;stopClock();if(reviewRunning&&reviewWorker){reviewWorker.terminate();reviewWorker=null;reviewRunning=false}initialMinutes=Number($('clock').value);game.reset();history=[];remaining={w:initialMinutes*60000,b:initialMinutes*60000};active='w';selected=null;legal=[];lastMove=null;started=false;finished=false;$('review').hidden=true;$('review-results').hidden=true;$('status').textContent='Trắng đi trước';render()}
function undo(){if(!history.length||remaining.w===0||remaining.b===0)return;stopClock();history.pop();const sans=history.map(x=>x.move.san);game.reset();history=[];for(const san of sans){const beforeFen=game.fen(),mover=game.turn(),move=game.move(san);if(move)history.push({move:{...move},beforeFen,afterFen:game.fen(),mover})}remaining={w:initialMinutes*60000,b:initialMinutes*60000};active=game.turn();selected=null;legal=[];lastMove=history.length?history[history.length-1].move:null;started=history.length>0;finished=false;$('review').hidden=true;$('review-results').hidden=true;if(started)startClock();render()}
function resign(){if(!started||finished)return;if(!confirm((active==='w'?'Trắng':'Đen')+' đầu hàng?'))return;finished=true;stopClock();$('status').textContent=(active==='w'?'Trắng':'Đen')+' đầu hàng — '+(active==='w'?'Đen':'Trắng')+' thắng';showReviewButton();render()}
function pgn(){return game.pgn({max_width:80,newline:'\n'})}
function toggleFullscreen(){const target=$('game-stage');if(document.fullscreenElement){document.exitFullscreen?.();return}if(target.requestFullscreen){target.requestFullscreen().catch(()=>{target.classList.toggle('expanded');$('zoom').textContent=target.classList.contains('expanded')?'Thu nhỏ bàn cờ':'⛶ Phóng to bàn cờ'})}else{target.classList.toggle('expanded');$('zoom').textContent=target.classList.contains('expanded')?'Thu nhỏ bàn cờ':'⛶ Phóng to bàn cờ'}}
document.addEventListener('fullscreenchange',()=>{$('zoom').textContent=document.fullscreenElement?'Thu nhỏ bàn cờ':'⛶ Phóng to bàn cờ'});
function reviewGame(){if(!finished){$('review-summary').textContent='Phân tích chỉ khả dụng sau khi ván cờ kết thúc.';return}if(!history.length){$('review-summary').textContent='Chưa có nước đi để phân tích.';$('review-results').hidden=false;return}if(reviewRunning)return;reviewRunning=true;$('review').disabled=true;$('review').textContent='Đang phân tích…';$('review-results').hidden=false;$('review-summary').textContent='Đang tải Stockfish. Phân tích từng nước đi có thể mất một lúc; đừng đóng trang.';$('review-list').innerHTML='';let index=0,results=[],worker;try{const engineBase=new URL('./stockfish/',window.location.href).href;const engineScript=engineBase+'stockfish-19-lite-single.js';const workerSource='var Module={locateFile:function(path){return "'+engineBase+'"+path;}};importScripts("'+engineScript+'");';worker=new Worker(engineScript);reviewWorker=worker}catch(e){finishReviewError('Không khởi động được Stockfish trong trình duyệt: '+e.message);return}
let phase='starting',current=null,bestCp=0,afterCp=0,bestMove='',timeout,startupTimeout;
const cleanup=()=>{clearTimeout(timeout);clearTimeout(startupTimeout);worker.terminate();reviewWorker=null;reviewRunning=false;$('review').disabled=false;$('review').textContent='Phân tích ván cờ'};
const fail=msg=>{cleanup();$('review-summary').textContent=msg+' Hãy kiểm tra kết nối mạng và thử lại.'};
worker.onerror=e=>fail('Lỗi tải engine Stockfish: '+(e.message||'không rõ nguyên nhân')+'.');
worker.onmessageerror=()=>fail('Không đọc được dữ liệu trả về từ Stockfish.');
worker.onmessage=e=>{const line=String(e.data||'');if(line==='uciok'){phase='checking';$('review-summary').textContent='Stockfish đã khởi động; đang chuẩn bị phân tích…';worker.postMessage('isready')}else if(line==='readyok'){clearTimeout(startupTimeout);if(index>=history.length){cleanup();renderReview(results);return}current=history[index];phase='before';bestCp=0;afterCp=0;bestMove='';$('review-summary').textContent='Đang phân tích '+(index+1)+'/'+history.length+' nước đi…';worker.postMessage('position fen '+current.beforeFen);worker.postMessage('go depth 12')}else if(line.startsWith('info ')&&line.includes(' score ')){const m=line.match(/\bscore (cp|mate) (-?\d+)/);if(m){const value=m[1]==='mate'?(Number(m[2])>0?10000:-10000):Number(m[2]);if(phase==='before')bestCp=value;else if(phase==='after')afterCp=value}}else if(line.startsWith('bestmove ')){if(phase==='before'){const bm=line.match(/^bestmove ([a-h][1-8][a-h][1-8][qrbn]?)/);bestMove=bm?bm[1]:'';phase='after';worker.postMessage('position fen '+current.afterFen);worker.postMessage('go depth 12')}else if(phase==='after'){const loss=Math.max(0,bestCp+afterCp);let label=loss<25?'Tốt':loss<80?'Khá tốt':loss<180?'Sai sót':loss<350?'Sai lầm':'Blunder';const played=current.move.from+current.move.to+(current.move.promotion||'');if(bestMove&&bestMove===played&&loss<80)label='Nước tốt nhất';results.push({n:index+1,color:current.mover==='w'?'Trắng':'Đen',san:current.move.san,loss,label,bestMove});index++;$('review-summary').textContent='Đã phân tích '+index+'/'+history.length+' nước đi…';phase='ready';worker.postMessage('isready')}}};
startupTimeout=setTimeout(()=>fail('Stockfish không khởi động trong 15 giây. Có thể file engine/WASM chưa tải được hoặc trình duyệt chặn Worker.'),15000);timeout=setTimeout(()=>fail('Phân tích quá lâu và đã bị dừng.'),300000);worker.postMessage('uci');
}
function finishReviewError(msg){reviewRunning=false;$('review').disabled=false;$('review').textContent='Phân tích ván cờ';$('review-results').hidden=false;$('review-summary').textContent=msg}
function renderReview(results){const sides={w:[],b:[]};for(const r of results)sides[r.color==='Trắng'?'w':'b'].push(r.loss);const avg=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:0;const accuracy=a=>100*Math.exp(-avg(a)/120);$('review-summary').textContent='Độ chính xác ước tính: Trắng '+accuracy(sides.w).toFixed(1)+'% · Đen '+accuracy(sides.b).toFixed(1)+'% · '+results.length+' nước phân tích ở depth 12. Chỉ số dựa trên mức mất điểm engine, không phải điểm chính thức của Chess.com/Lichess.';$('review-list').innerHTML='';for(const r of results){const row=document.createElement('div');row.className='review-row';const move=document.createElement('strong');move.textContent=r.n+'. '+r.color+' '+r.san;const tag=document.createElement('span');tag.className='review-tag '+(r.loss<80?'good':r.loss<180?'warn':'bad');tag.textContent=r.label+' · mất '+Math.round(r.loss)+' cp';row.append(move,tag);if(r.bestMove){const detail=document.createElement('small');detail.textContent='Nước engine đề xuất (UCI): '+r.bestMove;row.append(detail)}$('review-list').append(row)}}
$('new').addEventListener('click',newGame);$('resign').addEventListener('click',resign);$('flip').addEventListener('click',()=>{flipped=!flipped;render()});$('zoom').addEventListener('click',toggleFullscreen);$('clock').addEventListener('change',()=>{if(!started)newGame()});$('review').addEventListener('click',reviewGame);$('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(pgn());$('copy').textContent='Đã sao chép!';setTimeout(()=>$('copy').textContent='Sao chép PGN',1300)}catch{$('status').textContent='Không sao chép được; hãy tải PGN'}});$('download').addEventListener('click',()=>{const blob=new Blob([pgn()],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='covua-game.pgn';a.click();URL.revokeObjectURL(url)});newGame();

/* Online rooms: Firebase Realtime Database + anonymous sign-in. */
(function setupOnline(){
  const status=$('online-status'),createBtn=$('create-room'),joinBtn=$('join-room'),codeInput=$('room-code'),roleText=$('online-role');
  const startBtn=$('start-match'),promptBox=$('online-prompt'),offlineBtn=$('play-offline'),modePill=$('mode-pill');
  let db=null,uid=null,roomCode=null,role='local',appRef=null,roomRef=null,roomListener=null,onlineMode=false,roomState=null,applyingRemote=false,previousMatchStarted=false;
  const setStatus=s=>{if(status)status.textContent=s};
  const code=()=>Math.random().toString(36).slice(2,8).toUpperCase();
  const isOnline=()=>Boolean(onlineMode&&roomCode&&roomRef);
  const colorForUid=id=>roomState?.colorMap?.[id]||null;
  const canMove=turn=>!isOnline()||(Boolean(roomState?.matchStarted)&&((colorForUid(uid)==='w'&&turn==='w')||(colorForUid(uid)==='b'&&turn==='b')));
  function setMode(online){
    onlineMode=online;
    modePill.textContent=online?'ONLINE':'OFFLINE';
    modePill.classList.toggle('online',online);
    offlineBtn.classList.toggle('selected-mode',!online);
    startBtn.disabled=!online||!roomState||!roomState.whiteUid||!roomState.blackUid||Boolean(roomState.matchStarted);
    $('new').disabled=online;
    $('clock').disabled=online;
    $('resign').disabled=!online&&!started;
    if(!online){roleText.textContent='Chơi offline trên thiết bị này';promptBox.hidden=true;setStatus('Chế độ offline · không cần phòng mạng.')}
    roleLabel();
  }
  function roleLabel(){
    if(!roleText)return;
    if(!isOnline()){roleText.textContent='Chơi offline trên thiết bị này';return}
    if(role==='spectator')roleText.textContent='Bạn đang xem với tư cách khán giả';
    else if(!roomState?.matchStarted)roleText.textContent='Bạn đã vào phòng · chờ bắt đầu ván';
    else roleText.textContent=colorForUid(uid)==='w'?'Bạn cầm quân Trắng':colorForUid(uid)==='b'?'Bạn cầm quân Đen':'Bạn đang xem với tư cách khán giả';
  }
  function payload(){return {fen:game.fen(),sans:history.map(x=>x.move.san),started,finished,active,updatedAt:Date.now()}}
  async function publishPosition(){
    if(!isOnline()||applyingRemote||!roomState?.matchStarted||!['white','black'].includes(role))return;
    try{await roomRef.child('position').set(payload())}catch(e){setStatus('Không đồng bộ được nước đi: '+e.message)}
  }
  function applyPosition(data){
    if(!data||!data.fen)return;
    applyingRemote=true;
    try{
      game.reset();history=[];
      for(const san of (Array.isArray(data.sans)?data.sans:Object.values(data.sans||{}))){const beforeFen=game.fen(),mover=game.turn(),move=game.move(san);if(move)history.push({move:{...move},beforeFen,afterFen:game.fen(),mover})}
      if(game.fen()!==data.fen)game.load(data.fen);
      started=Boolean(data.started);finished=Boolean(data.finished);active=game.turn();selected=null;legal=[];lastMove=history.length?history[history.length-1].move:null;
      if(finished)stopClock();else if(started)startClock();else stopClock();
      render();showReviewButton();
    }catch(e){setStatus('Lỗi đồng bộ bàn cờ: '+e.message)}finally{applyingRemote=false}
  }
  function renderPrompt(){
    if(!isOnline()||!roomState){promptBox.hidden=true;return}
    const startReq=roomState.startRequest,undoReq=roomState.undoRequest;
    promptBox.innerHTML='';
    if(startReq&&!roomState.matchStarted){
      const mine=startReq.uid===uid;
      const p=document.createElement('p');p.textContent=mine?'Đã gửi lời mời. Đang chờ đối thủ chấp nhận…':'Đối thủ muốn bắt đầu ván đấu. Bạn có đồng ý không?';promptBox.append(p);
      if(!mine&&role!=='spectator'){
        const row=document.createElement('div');row.className='prompt-actions';
        const accept=document.createElement('button');accept.className='primary';accept.textContent='Chấp nhận';accept.onclick=acceptStart;
        const decline=document.createElement('button');decline.className='ghost';decline.textContent='Từ chối';decline.onclick=declineStart;
        row.append(accept,decline);promptBox.append(row);
      }
    }else if(undoReq&&!roomState.matchStarted===false){
      const mine=undoReq.uid===uid;
      const p=document.createElement('p');p.textContent=mine?'Đang chờ đối thủ đồng ý đi lại…':'Đối thủ yêu cầu đi lại một nước. Đồng ý hoàn tác?';promptBox.append(p);
      if(!mine&&role!=='spectator'){
        const row=document.createElement('div');row.className='prompt-actions';
        const accept=document.createElement('button');accept.className='primary';accept.textContent='Đồng ý đi lại';accept.onclick=acceptUndo;
        const decline=document.createElement('button');decline.className='ghost';decline.textContent='Không đồng ý';decline.onclick=declineUndo;
        row.append(accept,decline);promptBox.append(row);
      }
    }
    promptBox.hidden=!promptBox.childElementCount;
  }
  function watchRoom(ref){
    if(roomRef&&roomListener)roomRef.off('value',roomListener);
    roomRef=ref;roomListener=snap=>{
      const room=snap.val();if(!room){setStatus('Phòng không còn tồn tại.');return}
      const justStarted=Boolean(room.matchStarted)&&!previousMatchStarted;previousMatchStarted=Boolean(room.matchStarted);
      roomState=room;
      if(justStarted){initialMinutes=Number($('clock').value)||5;remaining={w:initialMinutes*60000,b:initialMinutes*60000};started=false;finished=false;active='w';stopClock();}
      window.__covuaWhiteUid=room.whiteUid||'';window.__covuaBlackUid=room.blackUid||'';
      if(uid===room.whiteUid||uid===room.blackUid){
        if(room.matchStarted&&room.colorMap)role=colorForUid(uid)==='w'?'white':colorForUid(uid)==='b'?'black':'spectator';
        else role=uid===room.whiteUid?'white':'black';
      }else role='spectator';
      setMode(true);
      const players=(room.blackUid?'Đủ 2 người chơi':'Đang chờ người chơi thứ hai');
      setStatus('Phòng '+roomCode+' · '+players+(room.matchStarted?' · Ván đang diễn ra':' · Chờ bắt đầu'));
      if(room.position)applyPosition(room.position);
      renderPrompt();
      startBtn.disabled=!room.whiteUid||!room.blackUid||Boolean(room.matchStarted)||role==='spectator';
      startBtn.textContent=room.matchStarted?'Ván đang diễn ra':'Bắt đầu ván';
      roleLabel();
    };
    roomRef.on('value',roomListener);
  }
  async function ready(){
    if(!window.firebase){setStatus('Không tải được Firebase SDK. Kiểm tra kết nối mạng.');throw new Error('Firebase SDK missing')}
    if(!appRef){
      const config={apiKey:'AIzaSyAO5tM89M6NPxlQe5zeDh_9-t6FHqaAcCs',authDomain:'chessweb-ff6b2.firebaseapp.com',databaseURL:'https://chessweb-ff6b2-default-rtdb.asia-southeast1.firebasedatabase.app',projectId:'chessweb-ff6b2',storageBucket:'chessweb-ff6b2.firebasestorage.app',messagingSenderId:'854820570620',appId:'1:854820570620:web:c4e92a4300f5e32ed19e79'};
      appRef=firebase.initializeApp(config);db=firebase.database();
    }
    const credential=await firebase.auth().signInAnonymously();uid=credential.user.uid;
  }
  async function createRoom(){
    createBtn.disabled=joinBtn.disabled=true;setStatus('Đang tạo phòng…');
    try{
      await ready();roomCode=code();onlineMode=true;
      const ref=db.ref('rooms/'+roomCode);
      await ref.set({whiteUid:uid,blackUid:'',createdAt:Date.now(),matchStarted:false,startRequest:null,undoRequest:null,colorMap:null,position:{fen:new Chess().fen(),sans:[],started:false,finished:false,active:'w'}});
      codeInput.value=roomCode;watchRoom(ref);
    }catch(e){onlineMode=false;setStatus('Tạo phòng thất bại: '+e.message+' — kiểm tra Database Rules.')}
    finally{createBtn.disabled=joinBtn.disabled=false}
  }
  async function joinRoom(){
    const requested=(codeInput.value||prompt('Nhập mã phòng')||'').trim().toUpperCase();if(!requested)return;
    if(!/^[A-Z0-9]{6,8}$/.test(requested)){setStatus('Mã phòng cần 6–8 ký tự chữ/số.');return}
    createBtn.disabled=joinBtn.disabled=true;setStatus('Đang tham gia phòng…');
    try{
      await ready();roomCode=requested;onlineMode=true;const ref=db.ref('rooms/'+roomCode);const snap=await ref.once('value');if(!snap.exists())throw new Error('Không tìm thấy phòng này');
      const current=snap.val();
      if(current.whiteUid===uid||current.blackUid===uid){watchRoom(ref);return}
      if(current.blackUid&&current.whiteUid){watchRoom(ref);return}
      const result=await ref.transaction(room=>{
        if(room===null)return;
        if(room.whiteUid===uid||room.blackUid===uid)return room;
        if(!room.blackUid){room.blackUid=uid;if(room.matchStarted!==true)room.matchStarted=false;return room}
        return;
      });
      if(!result.committed){
        const latest=await ref.once('value');
        if(!latest.exists())throw new Error('Phòng không còn tồn tại');
        watchRoom(ref);return;
      }
      watchRoom(ref);
    }catch(e){onlineMode=false;roomCode=null;setStatus('Tham gia thất bại: '+e.message+' — kiểm tra Rules hoặc mã phòng.')}
    finally{createBtn.disabled=joinBtn.disabled=false}
  }
  async function requestStart(){
    if(!isOnline()||role==='spectator'||!roomState?.blackUid){setStatus('Cần đủ hai người chơi trong phòng trước khi bắt đầu.');return}
    if(roomState.matchStarted)return;
    try{
      await roomRef.update({startRequest:{uid,at:Date.now()},undoRequest:null});
      setStatus('Đã gửi yêu cầu bắt đầu ván.');
    }catch(e){setStatus('Không gửi được yêu cầu: '+e.message)}
  }
  async function acceptStart(){
    if(!isOnline()||!roomState?.startRequest||roomState.startRequest.uid===uid)return;
    const whiteUid=roomState.whiteUid,blackUid=roomState.blackUid;
    const firstIsWhite=Math.random()<0.5;
    const colorMap={};
    colorMap[firstIsWhite?whiteUid:blackUid]='w';
    colorMap[firstIsWhite?blackUid:whiteUid]='b';
    try{
      await roomRef.update({matchStarted:true,colorMap,startRequest:null,undoRequest:null,position:{fen:new Chess().fen(),sans:[],started:false,finished:false,active:'w',updatedAt:Date.now()}});
      setStatus('Ván bắt đầu! Màu quân đã được chọn ngẫu nhiên.');
    }catch(e){setStatus('Không thể bắt đầu ván: '+e.message)}
  }
  async function declineStart(){try{await roomRef.update({startRequest:null});setStatus('Bạn đã từ chối lời mời.')}catch(e){setStatus('Không thể từ chối: '+e.message)}}
  async function requestUndo(){
    if(!isOnline()){undo();return}
    if(role==='spectator'){setStatus('Khán giả không thể yêu cầu đi lại.');return}
    if(!roomState?.matchStarted||finished||history.length===0){setStatus('Chưa có nước đi để yêu cầu hoàn tác.');return}
    if(roomState.undoRequest){setStatus('Đang có một yêu cầu đi lại chờ xử lý.');return}
    try{await roomRef.update({undoRequest:{uid,at:Date.now(),sans:history.slice(0,-1).map(x=>x.move.san)}});setStatus('Đã gửi yêu cầu đi lại.')}
    catch(e){setStatus('Không gửi được yêu cầu đi lại: '+e.message)}
  }
  async function acceptUndo(){
    const req=roomState?.undoRequest;if(!req||req.uid===uid)return;
    try{
      const temp=new Chess();const sans=Array.isArray(req.sans)?req.sans:Object.values(req.sans||{});
      for(const san of sans)temp.move(san);
      await roomRef.update({position:{fen:temp.fen(),sans,started:sans.length>0,finished:false,active:temp.turn(),updatedAt:Date.now()},undoRequest:null});
      setStatus('Hai bên đã đồng ý đi lại một nước.');
    }catch(e){setStatus('Không thể hoàn tác: '+e.message)}
  }
  async function declineUndo(){try{await roomRef.update({undoRequest:null});setStatus('Yêu cầu đi lại đã bị từ chối.')}catch(e){setStatus('Không thể từ chối: '+e.message)}}
  function enterOffline(){
    onlineMode=false;roomCode=null;roomState=null;role='local';selected=null;legal=[];
    stopClock();
    if(roomRef&&roomListener)roomRef.off('value',roomListener);
    roomRef=null;roomListener=null;
    setMode(false);newGame();render();
  }
  createBtn.addEventListener('click',createRoom);
  joinBtn.addEventListener('click',joinRoom);
  startBtn.addEventListener('click',requestStart);
  offlineBtn.addEventListener('click',enterOffline);
  $('undo').addEventListener('click',requestUndo);
  $('copy-room').addEventListener('click',async()=>{if(!roomCode)return;try{await navigator.clipboard.writeText(roomCode);$('copy-room').textContent='Đã chép';setTimeout(()=>$('copy-room').textContent='Chép mã',1200)}catch{codeInput.select();setStatus('Không tự chép được; hãy sao chép mã đang hiện.')}});
  codeInput.addEventListener('keydown',e=>{if(e.key==='Enter')joinBtn.click()});
  window.COVUA_ONLINE={isOnline,canMove,publishPosition};
  ready().then(()=>setStatus('Đã kết nối Firebase. Tạo phòng hoặc nhập mã; chơi offline vẫn dùng được.')).catch(e=>setStatus('Chưa kết nối Firebase: '+e.message));
})();

})();