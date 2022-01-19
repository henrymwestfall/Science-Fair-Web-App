var stateNumbersDiv


function toggleVisible(elemID) {
    let e = document.getElementById(elemID)
    e.hidden = !e.hidden
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


async function main() {
    const simState = await JSON.parse(await (await fetch(`/simulation-state/${apiKey}`)).text())
    updateAgentTable(simState)
}


window.onload = () => {
    stateNumbersDiv = document.getElementById("state-numbers")

    window.setInterval(main, 500)
}