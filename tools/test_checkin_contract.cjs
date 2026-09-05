// Unit-level contract tests for offline persistence/import logic; browser UI tested separately.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..'),plan=JSON.parse(fs.readFileSync(path.join(root,'docs/project_plan.json'),'utf8'));
let checks=0;
for(const member of plan.members){
 const html=fs.readFileSync(path.join(root,member.name,`打卡_${member.name}.html`),'utf8');
 const script=html.split('<script>')[1].split('</script>')[0], elements=new Map(), storage=new Map([[member.legacy_key,JSON.stringify({done:['old-1']})],[member.legacy_key+'_journal','old journal']]);
 const node=()=>({textContent:'',innerHTML:'',value:'',hidden:false,querySelectorAll:()=>[],classList:{toggle:()=>{}},files:[]});
 const doc={getElementById:id=>{if(!elements.has(id))elements.set(id,node());return elements.get(id)},querySelectorAll:()=>[]};doc.getElementById('plan-data').textContent=JSON.stringify(plan);
 const context={document:doc,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},Date,console,setTimeout,JSON,Set,Number,Object,Array,String,Error,assert};vm.createContext(context);vm.runInContext(script,context);
 vm.runInContext(`
 assert.equal(Object.keys(state.tasks).length,0);
 assert.equal(state.course.M01,undefined);
 assert.equal(legacy.state,JSON.stringify({done:['old-1']}));
 assert.equal(valid('tasks',{artifact:'',note:'test'}),false);
 assert.equal(valid('course',{video:'v',range:'t',minutes:'20',notes:'n',artifact:'f',answer:'a',viewed:true,recall:true,applied:false}),false);
 let test=blank();test.tasks['R2-'+MEMBER.code+'-W01']={artifact:'',note:'',status:'submitted'};
 assert.equal(clean(test).tasks['R2-'+MEMBER.code+'-W01'].status,'draft');
 let other={...test,member:'other'};assert.throws(()=>clean(other));
 let wrong={...test,revision:'old'};assert.throws(()=>clean(wrong));
 const attack='<img src=x onerror=alert(1)>';assert.equal(esc(attack),'&lt;img src=x onerror=alert(1)&gt;');
 test.tasks['R2-'+MEMBER.code+'-W01']={artifact:'file',note:'measured result',status:'submitted'};
 state=clean(test);persist();const roundtrip=clean(JSON.parse(localStorage.getItem(KEY)));assert.equal(roundtrip.tasks['R2-'+MEMBER.code+'-W01'].note,'measured result');
 assert.equal(localStorage.getItem(MEMBER.legacy_key),JSON.stringify({done:['old-1']}));
 test.history=Array.from({length:25},(_,i)=>({record:i}));assert.equal(clean(test).history.length,25);
 `,context);checks+=12;
}
console.log(JSON.stringify({passed:true,members:plan.members.length,checks,scope:'Import validation, required evidence, roundtrip, old-key preservation, escaping, no silent history truncation'}));
