const search_agents = document.getElementById('search_a');
search_agents.value = '';
const options = {
  shouldSort: true,
  threshold: 0.5,
  location: 0,
  distance: 30,
  maxPatternLength: 30,
  minMatchCharLength: 1,
  findAllMatches: true,
  ignoreFieldNorm: true,
  includeMatches: true,
  keys: ["d", "dd", "r", "h", "e"]
};
const re = new RegExp("\\d+$");
const alert_keys = [
  'Agent connection failed.',
  'Soft Quota has been reached.',
  'One or more selected devices not eligible.',
  'One or more selected devices failed backup.',
  'Errors encountered during backup.',
  'SQL databases not found.',
  'Failed to lock or flush one ore more devices.',
  'Backup Manager Policies are disabled.',
  'Hard Quota has been reached.',
  'Socket timed out.',
  'One or more parition table failed replication.',
  'One or more databases instance failed discovery.',
  'Failed to backup one or more devices.',
  'Disk Safe is closed.',
  'Unexpected error executing task.',
  'Problem checking disk usage.',
  'Not all recovery points were merged succesfully.',
  'One or more files failed restore.',
  'Could not verify recovery point.',
  'Main task interrupted.',
  'Failed to protect one or more control panel instances.',
  'Authenticate agent failed.',
  'Error getting device list.',
  'No eligible devices found.',
  'One or more databases failed to restore.',
  'Could not restore database.',
  'Unable to perform multi volume snapshot.',
  'Failed to restore one or more devices.',
  'Main task interrupted by unclean shutdown.',
  'Invalid policy.',
  'Device is below soft quota.',
  'Errors encountered while merging recovery point.',
];
let searched = false;
let on_enter = ['', ''];
let render_set = agents;
let height_fit = Math.floor((window.innerHeight - 115) / 124);
let width_fit = Math.floor((window.innerWidth - 225) / 332);
let tile_count = height_fit * width_fit;

const active_servers = [];
const servers_box = document.querySelectorAll('.servers_list')[0];
let s_i = 0;
//Build server list
for (const server of servers) {
  active_servers.push(s_i);
  const server_div = document.createElement('div');
  const server_title = document.createElement('a');
  server_title.tabIndex = 1;
  server_title.setAttribute('href', 'https://' + server[0] + '/');
  server_title.innerText = "r1server" + server[1];
  const server_btn = document.createElement('button');
  server_btn.classList.add('selected');
  server_btn.setAttribute("onclick", "toggle_server(" + s_i + ");");
  server_btn.innerText = '✓';
  server_div.classList.add('server');
  server_div.appendChild(server_title);
  server_div.appendChild(server_btn);
  servers_box.appendChild(server_div);
  s_i++;
}
const aside = document.querySelector('aside');
aside.tabIndex = 1;
const aside_btns = document.querySelectorAll('aside button');
for (const btn of aside_btns) {
  btn.tabIndex = 1;
}

const server_btns = document.querySelectorAll('.servers_list button');
function toggle_server(index) {
  if (active_servers.includes(index)) {
    server_btns[index].classList.remove('selected');
    const index_of = active_servers.indexOf(index);
    active_servers.splice(index_of, 1);
  } else {
    server_btns[index].classList.add('selected');
    active_servers.push(index);
  }
  render_agents(1);
}

const page_selectors = document.querySelectorAll(".page_select");
function page_select(page, page_count, selector, func) {
  const page_selector = page_selectors[selector];
  page_selector.innerHTML = "";
  if (page != 1) {
      const prev = document.createElement("button");
      prev.tabIndex = 1;
      prev.classList.add("prev");
      prev.classList.add("window_btn");
      prev.innerText = "< Prev";
      prev.setAttribute("onclick", func + (page - 1) + ");");
      page_selector.appendChild(prev);
  }
  const ellipsis = document.createElement("button");
  ellipsis.tabIndex = 1;
  ellipsis.innerText = "...";
  ellipsis.classList.add("window_nm");
  const end = document.createElement("button");
  end.tabIndex = 1;
  end.innerText = page_count;
  end.setAttribute("onclick", func + page_count + ");");
  end.classList.add("window_nm");
  const start = document.createElement("button");
  start.tabIndex = 1;
  start.innerText = 1;
  start.setAttribute("onclick", func + 1 + ");");
  start.classList.add("window_nm");
  if (page_count <= 5) {
    for (let i = 1; i <= page_count; i++) {
      const page_button = document.createElement("button");
      page_button.tabIndex = 1;
      if (i == page) {page_button.classList.add("nm_selected");}
      else {page_button.setAttribute("onclick", func + i + ");");}
      page_button.innerText = i;
      page_button.classList.add("window_nm");
      page_selector.appendChild(page_button);
    }
  } else {
    if (page <= 4) {
      for (let i = 1; i <= 4; i++) {
        const page_button = document.createElement("button");
        page_button.tabIndex = 1;
        if (i == page) {page_button.classList.add("nm_selected");}
        else {page_button.setAttribute("onclick", func + i + ");");}
        page_button.innerText = i;
        page_button.classList.add("window_nm");
        page_selector.appendChild(page_button);
      }
      page_selector.appendChild(ellipsis);
      page_selector.appendChild(end);
    } else if (page > page_count - 3) {
      page_selector.appendChild(start);
      page_selector.appendChild(ellipsis);
      for (let i = page_count - 3; i <= page_count; i++) {
        const page_button = document.createElement("button");
        page_button.tabIndex = 1;
        if (i == page) {page_button.classList.add("nm_selected");}
        else {page_button.setAttribute("onclick", func + i + ");");}
        page_button.innerText = i;
        page_button.classList.add("window_nm");
        page_selector.appendChild(page_button);
      }
    } else {
      page_selector.appendChild(start);
      page_selector.appendChild(ellipsis);
      for (let i = page - 1; i <= page + 1; i++) {
        const page_button = document.createElement("button");
        page_button.tabIndex = 1;
        if (i == page) {page_button.classList.add("nm_selected");}
        else {page_button.setAttribute("onclick", func + i + ");");}
        page_button.innerText = i;
        page_button.classList.add("window_nm");
        page_selector.appendChild(page_button);
      }
      ellipsis_clone = ellipsis.cloneNode(true);
      page_selector.appendChild(ellipsis_clone);
      page_selector.appendChild(end);
    }
  }
  if (page < page_count){
      const next = document.createElement("button");
      next.tabIndex = 1;
      next.classList.add("next");
      next.classList.add("window_btn");
      next.innerText = "Next >";
      next.setAttribute("onclick", func + (page + 1) + ");");
      page_selector.appendChild(next);
  }
}

let os_filter = 3;
const os_btns = document.querySelectorAll('#os_btns>button');
function toggle_os(key) {
  for (const btn of os_btns) {btn.classList.remove('selected');}
  if (key != os_filter) {
    os_btns[key].classList.add('selected');
    os_filter = key;
  } else {os_filter = 3;}
  render_agents(1);
}

let hw_filter = 3;
const hw_btns = document.querySelectorAll('#hw_btns>button');
function toggle_hw(key) {
  for (const btn of hw_btns) {btn.classList.remove('selected');}
  if (key != hw_filter) {
    hw_btns[key].classList.add('selected');
    hw_filter = key;
  } else {hw_filter = 3;}
  render_agents(1);
}

let state_filter = 3;
const state_btns = document.querySelectorAll('#state_btns>button');
function toggle_state(key) {
  for (const btn of state_btns) {btn.classList.remove('selected');}
  if (key != state_filter) {
    state_btns[key].classList.add('selected');
    state_filter = key;
  } else {state_filter = 3;}
  render_agents(1);
}

let error_filter = 3;
const error_btns = document.querySelectorAll('#error_btns>button');
function toggle_error(key) {
  for (const btn of error_btns) {btn.classList.remove('selected');}
  if (key != error_filter) {
    error_btns[key].classList.add('selected');
    error_filter = key;
  } else {error_filter = 3;}
  render_agents(1);
}

let run_filter = 3;
const run_btns = document.querySelectorAll('#run_btns>button');
function toggle_run(key) {
  for (const btn of run_btns) {btn.classList.remove('selected');}
  if (key != run_filter) {
    run_btns[key].classList.add('selected');
    run_filter = key;
  } else {run_filter = 3;}
  render_agents(1);
}

let sort_flag = false;
let sort_key = 0;
let sort_direction = false;
const sort_btns = document.querySelectorAll('#sorts button');
function sort_toggle(direction, key) {
  for (const btn of sort_btns) {btn.classList.remove('selected');}
  if (sort_direction == direction && sort_key == key) {
    sort_flag = false;
    sort_key = 0;
    sort_direction = false;
    render_agents(1);
    return;
  } else if(key == 3){
    if (direction == true) {sort_btns[0].classList.add('selected');}
    else{sort_btns[1].classList.add('selected');}
  } else if(key == 'used'){
    if (direction == true) {sort_btns[2].classList.add('selected');}
    else{sort_btns[3].classList.add('selected');}
  } else if(key == 4){
    if (direction == true) {sort_btns[4].classList.add('selected');}
    else{sort_btns[5].classList.add('selected');}
  } else if(key == 5){
    if (direction == true) {sort_btns[6].classList.add('selected');}
    else{sort_btns[7].classList.add('selected');}
  } else if(key == 'alpha'){
    if (direction == true) {sort_btns[8].classList.add('selected');}
    else{sort_btns[9].classList.add('selected');}
  }
  sort_flag = true;
  sort_key = key;
  sort_direction = direction;
  render_agents(1);
}

function filter_sort(pre_render) {
  const filter_set = [];
  for (const agent of pre_render) {

    //Flags into integer decoding.
    const run_state = (agent.n[2] % (2 ** 2)) - 1;
    const os_type = (agent.n[2] >> 2) % (2 ** 2);
    let error_state = (agent.n[2] >> 4) % 2;
    if (error_state == 0 && agent['a'] != undefined) {error_state = 2;}
    const hw_type = (agent.n[2] >> 5) % (2 ** 2);
    let state = ((agent.n[2] >> 7) % (2 ** 2));
    if (state == 3) {state = 1;}

    if (
      (os_filter == 3 || os_filter == os_type) &&
      (hw_filter == 3 || hw_filter == hw_type) &&
      (state_filter == 3 || state_filter == state) &&
      (error_filter == 3 || error_filter == error_state) &&
      (run_filter == 3 || run_filter == run_state) &&
      (active_servers.includes(agent.n[1]))
    ) {filter_set.push(agent);}
  }

  if (sort_flag && sort_key != 'used' && sort_key != 'alpha') {
    filter_set.sort(function (a, b){
      if (sort_direction) {return a.n[sort_key] - b.n[sort_key];}
      else {return b.n[sort_key] - a.n[sort_key];}
    });
  } else if (sort_flag && sort_key == 'used') {
    filter_set.sort(function (a, b){
      if (sort_direction) {return (a.n[3] / a.n[5]) - (b.n[3] / b.n[5]);}
      else {return (b.n[3] / b.n[5]) - (a.n[3] / a.n[5]);}
    });
  } else if (sort_flag && sort_key == 'alpha') {
    filter_set.sort(function (a, b){
      if (a['d'] == undefined) {a['d']='';}
      if (b['d'] == undefined) {b['d']='';}
      if (a['d'].toLowerCase() < b['d'].toLowerCase()) {
        if (sort_direction) {
          return -1;
        }
        return 1;
      } else if (a['d'].toLowerCase() > b['d'].toLowerCase()) {
        if (sort_direction) {
          return 1;
        }
        return -1;
      }
      return 0;
    });
  }
  return filter_set;
}


const agent_windows = document.querySelector("#agents_window section");
const uber = 'https://backup.manager.url/id=';
function render_agents(page) {
  const post_render = filter_sort(render_set);
  const count = tile_count;
  agent_windows.innerHTML = "";
  page_select(page, Math.ceil(post_render.length/count), 0, "render_agents(");
  let index = 0;
  for (let i = (page*count)-count; i < (page*count); i++) {
    if (i == post_render.length) {break;}
    const agent = post_render[i];
    const run_state = (agent.n[2] % (2 ** 2)) - 1;
    const os_type = (agent.n[2] >> 2) % (2 ** 2);
    let error_state = (agent.n[2] >> 4) % 2;
    if (error_state == 0 && agent['a'] != undefined) {error_state = 2;}
    const hw_type = (agent.n[2] >> 5) % (2 ** 2);
    const state = ((agent.n[2] >> 7) % (2 ** 2));

    const tile = document.createElement("div");
    const top = document.createElement("div");

    let text = '';
    if (agent.m_k != undefined) {
      const mark_start = "<span class=\"match\">";
      const mark_end = "</span>";
      text = agent.m_v;
      let offset = 0;
      for (let i = 0; i < agent.m_i.length; i++) {
        text = text.slice(0, agent.m_i[i][0] + offset) + mark_start + text.slice(agent.m_i[i][0] + offset);
        offset+=20;
        text = text.slice(0, agent.m_i[i][1] + offset + 1) + mark_end + text.slice(agent.m_i[i][1] + offset + 1);
        offset+=7;
      }
    }

    const des = document.createElement("a");
    des.tabIndex = -1;
    if (agent.m_k == 'd') {
      des.innerHTML = text;
    } else {
      des.innerText = agent['d'];
    }
    const agent_id = agent['d'].match(re);
    if (agent_id != null) {
      des.setAttribute('href', uber + agent_id[0]);
      tile.agent_id = agent_id[0];
    }
    des.style.float = 'left';
    top.appendChild(des);

    //Active state
    if (state == 3) { // Deleted
      des.classList.add('deleted');
      tile.classList.add('tile_deleted');
      const deleted = document.createElement("div");
      deleted.classList.add('icons');
      deleted.classList.add('icons_deleted');
      top.appendChild(deleted);
    } else if (state == 2) { // Orphaned
      des.classList.add('error');
      tile.classList.add('error');
      const orphan = document.createElement("div");
      orphan.classList.add('icons');
      orphan.classList.add('icons_orphan');
      top.appendChild(orphan);
    }

    //Error state
    if (error_state == 2 && run_state != 0) {
      des.classList.add('warn');
      tile.classList.add('tile_warn');
      const warn = document.createElement("div");
      warn.classList.add('icons');
      warn.classList.add('icons_warn');
      top.appendChild(warn);
    } else if (error_state == 1 && run_state != 0) {
      des.classList.add('error');
      tile.classList.add('tile_error');
      const error = document.createElement("div");
      error.classList.add('icons');
      error.classList.add('icons_error');
      top.appendChild(error);
    }

    //Running state
    const loader = document.createElement("div");
    loader.style.height = '29px';
    const animation = document.createElement("span");
    animation.style.margin = '1px 0 0 10px';
    loader.appendChild(animation);
    if (run_state == 0) { // Implicit check on if the variable exist.
      animation.classList.add('backup');
      top.appendChild(loader);
    } else if (run_state == 1) {
      animation.classList.add('merge');
      top.appendChild(loader);
    } else if (run_state == 2) {
      animation.classList.add('restore');
      top.appendChild(loader);
    }

    if (agent['a'] != undefined) {
      top.classList.add('tooltip');
      const alert_text = document.createElement("span");
      for (const alert of agent['a']) {
        alert_text.classList.add('tooltiptext2');
        alert_text.innerText += alert_keys[alert] + ' ';
      }
      top.appendChild(alert_text);
    }

    const server_ip = servers[agent.n[1]][0];
    const middle = document.createElement("div");
    middle.style.display = "flex";
    const server = document.createElement("a");
    server.tabIndex = -1;
    server.innerText = "r1server" + servers[agent.n[1]][1];
    server.setAttribute("href", 'https://' + server_ip + '/')
    middle.appendChild(server);
    let vm_set = false;
    if (hw_type == 1) {
      const vm = document.createElement("div");
      vm.classList.add('icons');
      vm.classList.add('icons_vm');
      middle.appendChild(vm);
      vm_set = true;
    }
    const os = document.createElement("div");
    if (os_type == 0) {
      os.classList.add('icons');
      os.classList.add('icons_windows');
    } else if (os_type == 1) {
      os.classList.add('icons');
      os.classList.add('icons_linux');
    }
    if (vm_set) {os.style.margin = '2px 0 0 10px';}
    middle.appendChild(os);

    const bottom = document.createElement("div");
    bottom.classList.add('load_parent');
    const load_bar = document.createElement("div");
    load_bar.classList.add('load_bar');
    const usage = document.createElement("p");

    let usage_text = '';
    if (agent.n[3] > 0) {
      if (agent.n[5] > 0) {
        usage_text = 'Used: ' + Math.round((agent.n[3] / agent.n[5]) * 100) + '% ';
        let decimal_place = 1;
        if (agent['hq'] > 8192) {
          decimal_place = 0;
        }
        usage_text += ' Soft: ' + (agent.n[4] / 1024).toFixed(decimal_place) + 'TB';
        usage_text += ' Hard: ' + (agent.n[5] / 1024).toFixed(decimal_place) + 'TB';
        if (agent.n[3] > (agent.n[5] * 0.9)) {
          load_bar.style.backgroundColor = '#CC2228';
        } else if (agent.n[3] > agent.n[4]) {
          load_bar.style.backgroundColor = '#CCAA00';
        } else {
          load_bar.style.backgroundColor = '#3D8C40';
        }
        load_bar.style.width = Math.round((agent.n[3] / agent.n[5]) * 100) + 2 + '%';
        bottom.appendChild(load_bar);
      } else {
        usage_text = 'Used: ' + (agent.n[3] / 1024).toFixed(2) + 'TB No quota!';
      }
      if (text != '' && agent.m_k != 'd') {
        usage.innerHTML = text;
      } else {
        usage.innerText = usage_text;
      }
      bottom.appendChild(usage);
    }

    tile.appendChild(top);
    tile.appendChild(middle);
    tile.appendChild(bottom);
    tile.server_ip = server_ip;
    tile.classList.add("tile");
    agent_windows.appendChild(tile);

    if (searched && index == 0) {
      tile.tabIndex = -1;
      tile.style.backgroundColor = "#191818";
      on_enter = [server_ip, agent_id[0]];
    } else {
      tile.tabIndex = 0;
    }

    index++;
  }
}

render_agents(1);

const fuse = new Fuse(agents, options);
search_agents.addEventListener("input", search_change);
function search_change(_e) {
  if (search_agents.value.replace(' ', '') == '') {
    render_set = agents;
    searched = false;
    render_agents(1);
    return;
  }
  const results = fuse.search(search_agents.value);
  const agents_set = [];
  for (const result of results) {
    const agent = JSON.parse(JSON.stringify(result.item));
    agent['m_k'] = result.matches[0].key;
    agent['m_i'] = result.matches[0].indices;
    agent['m_v'] = result.matches[0].value;
    agents_set.push(agent);
  }
  render_set = agents_set;
  searched = true;
  render_agents(1);
}

// Pressing enter
search_agents.addEventListener("keydown", search_enter);
const section = document.querySelector('section');
section.addEventListener("keydown", search_enter);
function search_enter(event) {
  if (search_agents.value.replace(' ', '') == '') {return;}
  if (event.key === "Enter") {
    let r1_url = '';
    let uber_url = uber;
    if (event.target.classList.contains('tile')) {
       r1_url = 'https://' + event.target.server_ip + '/';
       uber_url = uber + event.target.agent_id;
    } else {
       r1_url = 'https://' + on_enter[0] + '/';
       uber_url = uber + on_enter[1];
    }
    if (event.shiftKey) {
      if (event.ctrlKey) {window.open(uber_url, '_blank');}
      else {window.location = uber_url;}
    } else {
      if (event.ctrlKey) {window.open(r1_url, '_blank');}
      else {window.location = r1_url;}
    }
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Tab") {
    const first_tile = document.querySelector("section > .tile:first-child");
    if (first_tile.tabIndex == -1) {
      first_tile.style.backgroundColor = "";
      setTimeout(() => {
        first_tile.tabIndex = 0;
      }, 8);
    }
  }
});
