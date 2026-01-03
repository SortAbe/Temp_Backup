const pages = document.querySelectorAll("main");
const menu_buttons = document.querySelectorAll("#menu > button");
const searches = document.querySelectorAll(".search");
let reports_rendered = false;
function toggle_domain(page_num) {
  if (page_num == 0) {
    if (pages[0].style.display == "flex") {return;}
    searches[0].style.display = "block";
    searches[1].style.display = "none";
    pages[0].style.display = "flex";
    menu_buttons[0].classList.add("agents_s");
    pages[1].style.display = "none";
    menu_buttons[1].classList.remove("reports_s");
    pages[2].style.display = "none";
    menu_buttons[2].classList.remove("servers_s");
  } else if (page_num == 1) {
    if (pages[1].style.display == "flex") {return;}
    if (!reports_rendered) {
      render_reports(1);
      reports_rendered = ! reports_rendered;
    }
    searches[1].style.display = "block";
    searches[0].style.display = "none";
    menu_buttons[1].classList.add("reports_s");
    pages[0].style.display = "none";
    menu_buttons[0].classList.remove("agents_s");
    pages[1].style.display = "flex";
    pages[2].style.display = "none";
    menu_buttons[2].classList.remove("servers_s");
  } else {
    if (pages[2].style.display == "flex") {return;}
    searches[0].style.display = "none";
    searches[1].style.display = "none";
    menu_buttons[2].classList.add("servers_s");
    pages[0].style.display = "none";
    menu_buttons[0].classList.remove("agents_s");
    pages[1].style.display = "none";
    menu_buttons[1].classList.remove("reports_s");
    pages[2].style.display = "flex";
  }
}

const active_servers_r = [];
const servers_box_r = document.querySelectorAll('.servers_list')[1];
let sr_i = 0;
for (const server of servers) {
  active_servers_r.push(server);
  const server_div = document.createElement('div');
  const server_title = document.createElement('a');
  server_title.setAttribute('href', 'https://' + server[0] + '/');
  server_title.innerText = "r1server" + server[1];
  const server_btn_r = document.createElement('button');
  server_btn_r.classList.add('selected');
  server_btn_r.setAttribute("onclick", "toggle_server_r(" + sr_i + ");");
  server_btn_r.innerText = '✓';
  server_div.classList.add('server');
  server_div.appendChild(server_title);
  server_div.appendChild(server_btn_r);
  servers_box_r.appendChild(server_div);
  sr_i++;
}

const server_btns_r = document.querySelectorAll('#reports_window .servers_list button');
function toggle_server_r(server, index) {
  if (active_servers_r.includes(server)) {
    server_btns_r[index].classList.remove('selected');
    const i = active_servers_r.indexOf(server);
    active_servers_r.splice(i, 1);
  } else {
    server_btns_r[index].classList.add('selected');
    active_servers_r.push(server);
  }
  render_reports(1);
}

const reports_window = document.querySelector("#reports_window section");
function render_reports(page) {
  const post_render = reports_data;
  const count = tile_count;
  reports_window.innerHTML = "";
  page_select(page, Math.ceil(post_render.length/count), 1, "render_reports(");

  for (let i = (page*count)-count; i < (page*count); i++) {
    if (i == post_render.length) {break;} // In the event that page count is greater than data

    const report = post_render[i];
    const tile = document.createElement("div");

    const top = document.createElement("div");
    let text = '';
    if (report.m_k != undefined) {
      const mark_start = "<span class=\"match\">";
      const mark_end = "</span>";
      text = report.m_v;
      let offset = 0;
      for (let i = 0; i < report.m_i.length; i++) {
        text = text.slice(0, report.m_i[i][0] + offset) + mark_start + text.slice(report.m_i[i][0] + offset);
        offset+=20;
        text = text.slice(0, report.m_i[i][1] + offset + 1) + mark_end + text.slice(report.m_i[i][1] + offset + 1);
        offset+=7;
      }
    }

    const des = document.createElement("a");
    if (report.m_k == 'd') {
      des.innerHTML = text;
    } else {
      des.innerText = report['n'];
    }
    const cid = report['n'].match(re);
    if (cid != null) {
      des.setAttribute('href', 'https://backup.manager.url/id=' + cid[0]);
    }
    des.style.float = 'left';
    top.appendChild(des);

    //Error state
    if (report.r != undefined) {
      des.classList.add('error');
      tile.classList.add('tile_error');
      const error = document.createElement("div");
      error.classList.add('icons');
      error.classList.add('icons_error');
      top.appendChild(error);
      top.classList.add('tooltip');
      const alert_text = document.createElement("span");
      alert_text.classList.add('tooltiptext2');
      alert_text.innerText = report['r'];
      top.appendChild(alert_text);
    }

    tile.appendChild(top);

    const middle = document.createElement("div");
    const server = document.createElement("a");
    server.innerText = "r1server" + servers[report.s][1];
    server.setAttribute("href", 'https://' + servers[report.s][0] + '/')
    middle.appendChild(server);
    tile.appendChild(middle);

    const bot = document.createElement("div");
    const email = document.createElement("p");
    bot.classList.add('load_parent');
    if (report['e'].length > 0) {
      let first = true;
      for (const e of report['e']) {
        if (first) {
          email.innerText = e;
          first = false;
        } else {
          email.innerText += ', ' + e;
        }
      }
    }
    bot.appendChild(email);
    tile.appendChild(bot);

    tile.classList.add("tile");
    reports_window.appendChild(tile);
  }
}
