<script>
import Cli from "./Cli.svelte";let a=0
let b=0

function divide(a,b) {
let tmp=a%b
let tmp2=0
if (tmp!=0) {
tmp2=1
}
else if ((a%2)==1) {
tmp2=2
}
else  {
tmp2=3
}
return (a/b)+tmp2
}

async function main(__writeToCli,__readFromCli) {
while (true) {
let tmp=await __readFromCli()
if (tmp=="quit") {
break
}
__writeToCli(tmp+", dude")
}
for (
let i=0
; (i<5)
; i+=1) {
__writeToCli("bye bye")
}
return divide(a,b)
}

function logToConsole() {
console.log("suh dude")
}
</script><body><div class="take_input"><input type="number" bind:value="{a}" /><input type="number" bind:value="{b}" /><div class="output">{divide(a,b)}</div></div><div style="width: 50rem; height: 20rem;"><Cli main="{main}" /></div><div style="margin-top: 5rem;"><button on:click="{logToConsole}">Log</button></div></body>