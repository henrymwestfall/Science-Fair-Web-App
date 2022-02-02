var stateNumbersDiv
var doRefreshTable = false
var lastSeenStep = 0

function toggleVisible(elemID) {
    let e = document.getElementById(elemID)
    e.hidden = !e.hidden
}


function refresh() {
    doRefreshTable = true
}


async function main() {
    const simState = await JSON.parse(await (await fetch(`/simulation-state/${apiKey}`)).text())
    
    let secondsLeft = Math.floor(simState.stepEndTime - (new Date()).getTime() / 1000)
    if (secondsLeft < 0) secondsLeft = 0

    let secondsOnTime = secondsLeft % 60
    let minutesLeft = (secondsLeft - secondsOnTime) / 60

    let timeStr = ""
    if (secondsOnTime < 10) {
        timeStr = `${minutesLeft}:0${secondsOnTime}`
    } else {
        timeStr = `${minutesLeft}:${secondsOnTime}`
    }

    document.getElementById("sim-active").innerText = `Simulation Active: ${simState.error == null}`
    document.getElementById("sim-time").innerText = `Round Time Left: ${timeStr}`
    
    document.getElementById("step").innerHTML = `Round: ${simState.step}`

    if (simState.step != lastSeenStep) {
        lastSeenStep = simState.step
        doRefreshTable = true
    }

    if (doRefreshTable) {
        updateAgentTable(simState)
        doRefreshTable = false
    }
}


function stop() {
   window.open(`/past-simulations/${apiKey}`)
}


function pauseSimulation() {
    fetch(`/pause-simulation/${apiKey}`, {
        method: "POST",
        data: new FormData()
    }).then((response) => {
        response.text().then((text) => {
            const error = JSON.parse(text).error
            if (error != null) alert(error)
        })
    })
}


function resumeSimulation() {
    fetch(`/resume-simulation/${apiKey}`, {
        method: "POST",
        data: new FormData()
    }).then((response) => {
        response.text().then((text) => {
            const error = JSON.parse(text).error
            if (error != null) alert(error)
        })
    })
}


function updateAgentTable(state) {
    const table = document.getElementById("agent-table")
    const rows = Array.from(table.children).slice(1)
    const numCols = state.agentData[0].length

    for (let i = 0; i < state.agentData.length; i++) {
        if (rows.length <= i) {
            var tr = document.createElement("tr")
            
            for (let c = 0; c < numCols; c++) {
                tr.appendChild(document.createElement("td"))
            }
            
            table.appendChild(tr)
        } else var tr = rows[i]

        for (let j = 0; j < numCols; j++) {
            tr.children[j].innerHTML = state.agentData[i][j]
        }
    }
}


function updateStateNumbers() {
    
}


window.onload = () => {
    stateNumbersDiv = document.getElementById("state-numbers")
    window.setInterval(main, 500)
}