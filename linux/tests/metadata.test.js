const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const bridge = fs.readFileSync(path.join(__dirname, '..', 'metadata-bridge.js'), 'utf8');
const message = title => JSON.stringify({type:6,args:['media.metadata',{title,artist:'Series'}]});
const tick = () => new Promise(resolve => setImmediate(resolve));
function setup(getState) {
    const output = [];
    const context = vm.createContext({window:{core:{getState}},location:{hash:'#/player/stream/addon/meta/series/tt1234/tt1234%3A1%3A1'},
        fetch:()=>{throw Error('Network access is forbidden in this bridge');}});
    vm.runInContext(bridge, context);
    const emit = vm.runInContext('enrichDiscordMetadata', context);
    return {context, output, send:value=>emit(value,packet=>output.push(JSON.parse(packet).args[1]))};
}
function player(videoId='tt1234:1:1') {
    return {metaItem:{type:'Ready',content:{id:'tt1234',type:'series',name:'Series',releaseInfo:'2024',poster:'https://example.com/poster.jpg',
        videos:[{id:videoId,title:'Pilot',season:1,episode:1,thumbnail:'https://example.com/episode.jpg'}]}},
        selected:{metaRequest:{path:{id:'tt1234',type:'series'}},streamRequest:{path:{id:videoId}}}};
}
test('uses already-loaded poster and episode metadata without network requests',async()=>{
    const state=setup(async model=>{assert.equal(model,'player');return player();});
    state.send(message('Pilot (1x1)')); await tick();
    assert.equal(state.output.length,1);
    assert.equal(state.output[0].name,'Series');
    assert.equal(state.output[0].episode,'Pilot (S1 · E1)');
    assert.equal(state.output[0].poster,'https://example.com/poster.jpg');
    assert.equal(state.output[0].thumbnail,'https://example.com/episode.jpg');
});
test('drops stale results after navigation or newer metadata',async()=>{
    const resolves=[];
    const state=setup(()=>new Promise(resolve=>resolves.push(resolve)));
    state.send(message('Pilot')); await tick();
    state.send(message('New title')); await tick();
    resolves[0](player()); await tick(); assert.equal(state.output.length,0);
    state.context.location.hash='#/board';
    resolves[1](player()); await tick(); assert.equal(state.output.length,0);
});
test('does not attach an older player snapshot to another episode',async()=>{
    const state=setup(async()=>player('tt1234:1:2'));
    state.send(message('Pilot'));await tick();assert.equal(state.output.length,0);
});
test('missing core, unloaded models and rejected snapshots preserve basic presence',async()=>{
    for (const getState of [undefined,async()=>({metaItem:{type:'Loading'}}),async()=>{throw Error('reload');}]) {
        const state=setup(getState); state.send(message('Pilot'));await tick();assert.equal(state.output.length,0);
    }
});
test('ignores malformed or unrelated IPC messages',async()=>{
    const state=setup(async()=>player());
    for(const value of ['bad JSON','{}',JSON.stringify({type:6,args:['media.status',{paused:true}]}),JSON.stringify({type:6,args:['media.metadata',{}]})]) state.send(value);
    await tick();assert.equal(state.output.length,0);
});
