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
function showReviewButton(){const b=$('review');if(b)b.hidden=history.length===0}
function afterMove(){started=true;active=game.turn();if(game.game_over()){finished=true;stopClock();showReviewButton()}else startClock();render();if(window.COVUA_ONLINE?.isOnline())window.COVUA_ONLINE.publishPosition()}
function newGame(){stopClock();if(reviewRunning&&reviewWorker){reviewWorker.terminate();reviewWorker=null;reviewRunning=false}initialMinutes=Number($('clock').value);game.reset();history=[];remaining={w:initialMinutes*60000,b:initialMinutes*60000};active='w';selected=null;legal=[];lastMove=null;started=false;finished=false;$('review').hidden=true;$('review-results').hidden=true;$('status').textContent='Trắng đi trước';render()}
function undo(){if(!history.length||remaining.w===0||remaining.b===0)return;stopClock();history.pop();const sans=history.map(x=>x.move.san);game.reset();history=[];for(const san of sans){const beforeFen=game.fen(),mover=game.turn(),move=game.move(san);if(move)history.push({move:{...move},beforeFen,afterFen:game.fen(),mover})}remaining={w:initialMinutes*60000,b:initialMinutes*60000};active=game.turn();selected=null;legal=[];lastMove=history.length?history[history.length-1].move:null;started=history.length>0;finished=false;$('review').hidden=true;$('review-results').hidden=true;if(started)startClock();render()}
function resign(){if(!started||finished)return;if(!confirm((active==='w'?'Trắng':'Đen')+' đầu hàng?'))return;finished=true;stopClock();$('status').textContent=(active==='w'?'Trắng':'Đen')+' đầu hàng — '+(active==='w'?'Đen':'Trắng')+' thắng';showReviewButton();render()}
function pgn(){return game.pgn({max_width:80,newline:'\n'})}
function toggleFullscreen(){const target=$('game-stage');if(document.fullscreenElement){document.exitFullscreen?.();return}if(target.requestFullscreen){target.requestFullscreen().catch(()=>{target.classList.toggle('expanded');$('zoom').textContent=target.classList.contains('expanded')?'Thu nhỏ bàn cờ':'⛶ Phóng to bàn cờ'})}else{target.classList.toggle('expanded');$('zoom').textContent=target.classList.contains('expanded')?'Thu nhỏ bàn cờ':'⛶ Phóng to bàn cờ'}}
document.addEventListener('fullscreenchange',()=>{$('zoom').textContent=document.fullscreenElement?'Thu nhỏ bàn cờ':'⛶ Phóng to bàn cờ'});
function reviewGame(){if(!history.length){$('review-summary').textContent='Chưa có nước đi để phân tích.';$('review-results').hidden=false;return}if(reviewRunning)return;reviewRunning=true;$('review').disabled=true;$('review').textContent='Đang phân tích…';$('review-results').hidden=false;$('review-summary').textContent='Đang tải Stockfish. Phân tích từng nước đi có thể mất một lúc; đừng đóng trang.';$('review-list').innerHTML='';let index=0,results=[],worker;try{const engineBase=new URL('./stockfish/',window.location.href).href;const engineScript=engineBase+'stockfish-19-lite-single.js';const workerSource='var Module={locateFile:function(path){return "'+engineBase+'"+path;}};importScripts("'+engineScript+'");';worker=new Worker(engineScript);reviewWorker=worker}catch(e){finishReviewError('Không khởi động được Stockfish trong trình duyệt: '+e.message);return}
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
$('new').addEventListener('click',newGame);$('undo').addEventListener('click',undo);$('resign').addEventListener('click',resign);$('flip').addEventListener('click',()=>{flipped=!flipped;render()});$('zoom').addEventListener('click',toggleFullscreen);$('clock').addEventListener('change',()=>{if(!started)newGame()});$('review').addEventListener('click',reviewGame);$('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(pgn());$('copy').textContent='Đã sao chép!';setTimeout(()=>$('copy').textContent='Sao chép PGN',1300)}catch{$('status').textContent='Không sao chép được; hãy tải PGN'}});$('download').addEventListener('click',()=>{const blob=new Blob([pgn()],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='covua-game.pgn';a.click();URL.revokeObjectURL(url)});newGame();

/* Online rooms: Firebase Realtime Database + anonymous sign-in. */
(function setupOnline(){
  const status=$('online-status'),createBtn=$('create-room'),joinBtn=$('join-room'),wrap=$('room-code-wrap'),codeInput=$('room-code'),roleText=$('online-role');
  let db=null,uid=null,roomCode=null,role='local',appRef=null,applyingRemote=false,roomRef=null,roomListener=null;
  const setStatus=(s)=>{if(status)status.textContent=s};
  const code=()=>Math.random().toString(36).slice(2,8).toUpperCase();
  const isOnline=()=>Boolean(roomCode&&roomRef);
  const canMove=(turn)=>!isOnline()||(role==='white'&&turn==='w'&&uid===window.__covuaWhiteUid)||(role==='black'&&turn==='b'&&uid===window.__covuaBlackUid);
  function roleLabel(){roleText.textContent=!isOnline()?'':role==='spectator'?'Bạn đang xem với tư cách khán giả':role==='white'?'Bạn cầm quân Trắng':role==='black'?'Bạn cầm quân Đen':'Đang kết nối phòng'}
  function payload(){return {fen:game.fen(),sans:history.map(x=>x.move.san),started,finished,active,updatedAt:Date.now()}}
  async function publishPosition(){
    if(!isOnline()||applyingRemote||!(role==='white'||role==='black'))return;
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
      if(finished)stopClock();else if(started)startClock();render();showReviewButton();
    }catch(e){setStatus('Lỗi đồng bộ bàn cờ: '+e.message)}finally{applyingRemote=false}
  }
  function watchRoom(ref){
    if(roomRef&&roomListener)roomRef.off('value',roomListener);
    roomRef=ref;roomListener=snap=>{
      const room=snap.val();if(!room){setStatus('Phòng không còn tồn tại.');return}
      window.__covuaWhiteUid=room.whiteUid||'';window.__covuaBlackUid=room.blackUid||'';
      if(uid===room.whiteUid)role='white';else if(uid===room.blackUid)role='black';else role='spectator';
      wrap.hidden=false;codeInput.value=roomCode;roleLabel();
      const players=(room.blackUid?'Đủ 2 người chơi':'Đang chờ người chơi Đen');
      setStatus('Phòng '+roomCode+' · '+players+' · Khán giả có thể vào xem.');
      if(room.position)applyPosition(room.position);
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
  createBtn.addEventListener('click',async()=>{
    createBtn.disabled=joinBtn.disabled=true;setStatus('Đang tạo phòng…');
    try{await ready();roomCode=code();const ref=db.ref('rooms/'+roomCode);await ref.set({whiteUid:uid,blackUid:'',createdAt:Date.now(),position:{fen:new Chess().fen(),sans:[],started:false,finished:false,active:'w'}});watchRoom(ref)}
    catch(e){setStatus('Tạo phòng thất bại: '+e.message+' — hãy kiểm tra Anonymous Auth và Database Rules.')}
    finally{createBtn.disabled=joinBtn.disabled=false}
  });
  joinBtn.addEventListener('click',async()=>{
    const requested=(codeInput.value||prompt('Nhập mã phòng')).trim().toUpperCase();if(!requested)return;
    if(!/^[A-Z0-9]{6,8}$/.test(requested)){setStatus('Mã phòng cần 6–8 ký tự chữ/số.');return}
    createBtn.disabled=joinBtn.disabled=true;setStatus('Đang tham gia phòng…');
    try{
      await ready();roomCode=requested;const ref=db.ref('rooms/'+roomCode);const snap=await ref.once('value');if(!snap.exists())throw new Error('Không tìm thấy phòng này');
      const result=await ref.transaction(room=>{
        if(room===null)return;
        if(room.whiteUid===uid||room.blackUid===uid)return room;
        if(!room.blackUid){room.blackUid=uid;return room}
        return room;
      });
      if(!result.committed)throw new Error('Không thể vào phòng');
      watchRoom(ref);
    }catch(e){roomCode=null;setStatus('Tham gia thất bại: '+e.message+' — nếu là lỗi permission, hãy cập nhật Rules.')}
    finally{createBtn.disabled=joinBtn.disabled=false}
  });
  $('copy-room').addEventListener('click',async()=>{if(!roomCode)return;try{await navigator.clipboard.writeText(roomCode);$('copy-room').textContent='Đã chép';setTimeout(()=>$('copy-room').textContent='Chép mã',1200)}catch{codeInput.select();setStatus('Không tự chép được; hãy sao chép mã đang hiện.') }});
  codeInput.addEventListener('keydown',e=>{if(e.key==='Enter')joinBtn.click()});
  // Clicking "Nhập mã" without text asks for the code; also supports pasting directly.
  window.COVUA_ONLINE={isOnline,canMove,publishPosition};
  ready().then(()=>setStatus('Đã kết nối Firebase. Tạo phòng mới hoặc nhập mã phòng.')).catch(e=>setStatus('Chưa kết nối Firebase: '+e.message));
})();

})();