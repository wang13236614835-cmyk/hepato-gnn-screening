/* 2026-10-12 CURRENT专项打卡叠层。独立于旧16周完成键；个人自报不产生科研Gate/真人签核。 */
(function () {
  "use strict";
  var people = {
    "王启龙": [["制定/冻结五MCULE评分协议","跨人复核历史计算分与适用域"],["确认老药库2973/4225差异和任务分工","抽核老药反向命中与拒判"],["复查中药37成分与老药评分一致性","协调跨库靶点争议"],["汇总三路证据和三库状态","提交导师图与下一轮决策"]],
    "宁显泷": [["模型资格与评分/AD/UQ边界","同折模型指标及拒判一致性"],["老药多靶点推理、版本记录","检查外推/不确定性/失败案例"],["中药靶点预测与模型域内检查","交叉比较老药/中药可比靶点"],["独立复算三路评分与拒判","模型版本/seed/hash/局限交付"]],
    "衣思淼": [["五MCULE结构、手性和身份核验","打分输入及缺失值与来源字典"],["核老药2973/4225来源纳排","药品批准地区/撤市及结构清洗"],["37成分结构、植物来源核验","中药去重/PAINS/缺失项表"],["三路身份与纳排记录对账","数据字典与哈希核验"]],
    "代维斯丹": [["旧Vina/ADMET工件逐项对应评分","结构支持与模型活性区分复核"],["核老药结构/盐型与靶点相关证据","复查结构假阳性和不合理结合"],["中药结构/PAINS/ADMET检查","对接及结构支持可重复性抽检"],["交付结构验证与负例分析","整理不能外推为疗效的结论"]],
    "王散曼": [["五MCULE文献/先例/反证分级","跨人核验评分所用靶点证据"],["老药药理/适应证与MASH文献审查","区分直接药理与疾病假说"],["中药来源/靶点/疾病文献分层","核对中药肝病场景与反证"],["统一三路主张证据矩阵","稿件/专利可写不可写审查"]]
  };
  var codes = {"王启龙":"Q","宁显泷":"N","衣思淼":"Y","代维斯丹":"D","王散曼":"S"};
  var title = document.title || "";
  var name = Object.keys(people).filter(function(n) { return title.indexOf(n) >= 0; })[0];
  var anchor = document.getElementById("app");
  if (!name || !anchor || document.getElementById("aidd20261012")) return;
  var storeKey = "aidd-four-week-sprint-20261012:" + name; // 保留旧三周自评，不继承完成
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(storeKey) || "{}"); } catch (e) { saved = {}; }
  var dates = [["10/12–10/18","W1 打分"],["10/19–10/25","W2 老药反向筛选"],["10/26–11/01","W3 中药反向筛选"],["11/02–11/08","W4 收尾"]];
  var css = document.createElement("style");
  css.textContent = "#aidd20261012{max-width:1080px;margin:18px auto 0;padding:0 18px}#aidd20261012 .sprint-card{padding:18px 20px;background:#fff;border:2px solid #3568a8;border-radius:12px;box-shadow:0 2px 6px #0001}#aidd20261012 h2{margin:0 0 8px;color:#21528f;font-size:18px}#aidd20261012 .small{color:#566477;font-size:13px;line-height:1.7}#aidd20261012 .wk{border-top:1px solid #dce4ed;padding-top:12px;margin-top:12px}#aidd20261012 .taskrow{display:grid;grid-template-columns:minmax(150px,2fr) minmax(140px,1.2fr) minmax(145px,1fr);gap:8px;align-items:center;margin:10px 0}#aidd20261012 input,#aidd20261012 select{min-width:0;width:100%;padding:7px;border:1px solid #cbd5e1;border-radius:6px;background:#fff;font-size:13px}#aidd20261012 .actions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}#aidd20261012 button{border:1px solid #2b5fa8;background:#f5f9ff;color:#22518c;border-radius:7px;padding:7px 12px;cursor:pointer}#aidd20261012 .tasklabel{font-size:13px}#aidd20261012 .tasklabel b{display:block;color:#365a83}#aidd20261012 .warn{padding:9px;background:#fff7e6;color:#7a4b10;border-radius:7px;font-size:12px}#aidd20261012 .hintstatus{font-size:12px;color:#426b4b}@media(max-width:680px){#aidd20261012 .taskrow{grid-template-columns:1fr}#aidd20261012 .taskrow input,#aidd20261012 .taskrow select{font-size:14px}}";
  document.head.appendChild(css);
  var wrapper = document.createElement("section"); wrapper.id = "aidd20261012";
  var card = document.createElement("div"); card.className = "sprint-card";
  wrapper.appendChild(card);
  var h = document.createElement("h2"); h.textContent = "当前专项打卡 · 2026-10-12 至 11-08 · " + name; card.appendChild(h);
  var info = document.createElement("p"); info.className = "small";
  info.textContent = "四周计划：W1打分→W2老药反向筛选→W3中药反向筛选→W4收尾。旧16周学习打卡与旧三周记录保留但不继承；科学Gate由V4原始证据和真人受控复核裁决。"; card.appendChild(info);
  var plan = document.createElement("a"); plan.href="../docs/CURRENT_SPRINT_20261012.md"; plan.textContent="查看四周任务与评分/筛选验收"; plan.className="small";card.appendChild(plan);
  var warn=document.createElement("p");warn.className="warn";warn.textContent="“已提交待复核”必须填实际原始证据路径/DOI；仍不等于人审通过、实验执行或候选发布。无法核实时选择“缺原件/阻塞”，不得伪造通过。";card.appendChild(warn);
  function persist() { try { localStorage.setItem(storeKey,JSON.stringify(saved)); }catch(e){ alert("本地存储失败，请导出记录。"); } }
  function field(type, key, label) {
    var node=document.createElement(type);
    if(type==="select") {
      [["PENDING","未开始"],["IN_PROGRESS","核验中"],["NEEDS_EVIDENCE","缺原件/阻塞"],["SUBMITTED_FOR_REVIEW","已提交待复核"]].forEach(function(z){var opt=document.createElement("option"); opt.value=z[0];opt.textContent=z[1];node.appendChild(opt);});
      node.value=(saved[key]||{}).status||"PENDING";
      node.addEventListener("change",function(){
        var v=node.value, record=saved[key]||{};
        if(v==="SUBMITTED_FOR_REVIEW" && !(record.evidence||"").trim()){alert("需先填写真实证据路径或DOI/PMID。");node.value=record.status||"PENDING";return;}
        record.status=v;record.updated=new Date().toISOString();saved[key]=record;persist();
      });
    } else {
      node.type="text";node.placeholder=label;
      node.value=(saved[key]||{}).evidence||"";
      node.addEventListener("change",function(){
        var record=saved[key]||{};record.evidence=node.value.trim();
        if(!record.evidence && record.status==="SUBMITTED_FOR_REVIEW"){record.status="NEEDS_EVIDENCE";if(node.previousSibling && node.previousSibling.tagName==="SELECT")node.previousSibling.value=record.status;}
        record.updated=new Date().toISOString();saved[key]=record;persist();
      });
    } return node;
  }
  var now = new Date(), dateValue = now.getFullYear()*10000+(now.getMonth()+1)*100+now.getDate();
  dates.forEach(function(d,i){
    var section=document.createElement("div");section.className="wk";
    var title=document.createElement("h3");title.textContent="W"+(i+1)+" | "+d[0]+" | "+d[1]+(dateValue >= [20261012,20261019,20261026,20261102][i] && dateValue <= [20261018,20261025,20261101,20261108][i]?"（本周）":"");section.appendChild(title);
    people[name][i].forEach(function(task,j){
      var key="W"+(i+1)+"-"+codes[name]+"."+(j+1), row=document.createElement("div");row.className="taskrow";
      var label=document.createElement("div");label.className="tasklabel";
      var bold=document.createElement("b");bold.textContent=key;label.appendChild(bold);
      label.appendChild(document.createTextNode(task));row.appendChild(label);
      var select=field("select",key,"");select.setAttribute("aria-label",key+"进度");row.appendChild(select);
      var input=field("input",key,"原始文件/DOI/PMID");input.setAttribute("aria-label",key+"证据路径");row.appendChild(input);
      section.appendChild(row);
    });card.appendChild(section);
  });
  var actions=document.createElement("div");actions.className="actions";
  var exportBtn=document.createElement("button");exportBtn.type="button";exportBtn.textContent="导出本人的专项打卡JSON";
  exportBtn.addEventListener("click",function(){
    var data={plan:"AIDD-CURRENT-FOUR-WEEK-20261012",member:name,scope:"PERSONAL_SELF_CHECK_NOT_AUTHORITY",exported_at:new Date().toISOString(),items:saved};
    var file=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
    var url=URL.createObjectURL(file),a=document.createElement("a");a.href=url;a.download="W1-W4_自评打卡_"+name+".json";a.click();setTimeout(function(){URL.revokeObjectURL(url);},1000);
  });
  actions.appendChild(exportBtn);card.appendChild(actions);
  var foot=document.createElement("div");foot.className="hintstatus";foot.textContent="保存位置：本机浏览器 localStorage；跨电脑需导出文件。正式科研签核仍需原始来源、独立交叉复核、受控导入与真实审批。";card.appendChild(foot);
  anchor.parentNode.insertBefore(wrapper,anchor);
})();