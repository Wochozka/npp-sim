const sock = io();
const buf = [];
const maxN = 1000;
const cvs = document.getElementById('chartP');
const ctx = cvs.getContext('2d');


let state = {};


function draw(){
ctx.clearRect(0,0,cvs.width,cvs.height);
if(buf.length < 2) return;
const min = Math.min(...buf.map(b=>b.P), 0);
const max = Math.max(...buf.map(b=>b.P), 3);
const sx = cvs.width/(maxN-1);
const sy = max>min ? cvs.height/(max-min) : 1;
ctx.beginPath();
buf.forEach((b,i)=>{
const x = i*sx;
const y = cvs.height - (b.P-min)*sy;
if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
});
ctx.stroke();
}


sock.on('state', s => {
state = s;
document.getElementById('pP').textContent = s.P.toFixed(3);
document.getElementById('pRho').textContent = s.rho.toExponential(3);
document.getElementById('pT').textContent = s.T_fuel.toFixed(1);
document.getElementById('pRod').textContent = s.rod_pos.toFixed(3);
document.getElementById('pFlow').textContent = s.coolant_flow.toFixed(3);
document.getElementById('pScram').textContent = s.scrammed ? 'YES' : 'NO';


buf.push({P:s.P});
if(buf.length>maxN) buf.shift();
draw();
});


async function cmd(name, args={}){
const r = await fetch('/api/command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({cmd:name, args})});
const j = await r.json();
return j;
}


const powerSp = document.getElementById('power_sp');
const flowSp = document.getElementById('flow_sp');
const vP = document.getElementById('v_power_sp');
const vF = document.getElementById('v_flow_sp');


powerSp.addEventListener('input', e=>{
const v = parseFloat(e.target.value);
vP.textContent = v.toFixed(2);
cmd('set_power_sp', {value:v});
});


flowSp.addEventListener('input', e=>{
const v = parseFloat(e.target.value);
vF.textContent = v.toFixed(2);
cmd('set_flow_sp', {value:v});
});


(async()=>{
const r = await fetch('/api/state');
const s = await r.json();
vP.textContent = s.power_sp.toFixed(2);
vF.textContent = s.flow_sp.toFixed(2);
powerSp.value = s.power_sp;
flowSp.value = s.flow_sp;
})();
