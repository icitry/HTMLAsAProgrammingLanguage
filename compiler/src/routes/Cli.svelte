<script>
    import { onMount } from "svelte";
    import { writable } from "svelte/store";

    export let main;

    let cli_write = writable("");
    let cli_read = writable("");
    let cli_read_enter = writable(false);

    let shouldReadReturn = false;

    cli_read_enter.subscribe((value) => {
        if (value) {
            shouldReadReturn = true;
        }
    });

    function read_from_cli(...args) {
        const readPromise = new Promise(async (resolve, reject) => {
            while (!shouldReadReturn) {
                await new Promise((r) => setTimeout(r, 500));
            }
            shouldReadReturn = false;
            let tmp = $cli_read;
            cli_read.set("");
            cli_read_enter.set(false);
            resolve(tmp);
        });
        return readPromise;
    }

    function write_to_cli(...args) {
        for (let i = 0; i < args.length; i++) {
            cli_write.update((val) => val + args[i] + "\n");
        }
    }

    onMount(() => {
        main(write_to_cli, read_from_cli);
    });
</script>

<div class="cli">
    <textarea readonly="true" bind:value={$cli_write} /><input
        type="text"
        bind:value={$cli_read}
        on:keydown={(e) => {
            if (e.key === "Enter") {
                cli_read_enter.set(true);
            }
        }}
    />
</div>

<style>
    .cli {
        min-height: 10rem;
        height: 100%;
        width: 100%;
    }

    .cli textarea {
        height: 90%;
        width: 100%;
        resize: none;
    }

    .cli input {
        height: 10%;
        width: 100%;
    }
</style>
