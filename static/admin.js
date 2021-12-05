var stateNumbersDiv


function toggleVisible(elemID) {
    let e = document.getElementById(elemID)
    e.hidden = !e.hidden
}


function updateAPIKeyTable(state) {
    const table = document.getElementById("api-key-table")
    const rows = Array.from(table.children).slice(1)

    for (let i = 0; i < state.apiKeys.length; i++) {
        if (rows.length <= i) {
            var tr = document.createElement("tr")
            var keyCell = document.createElement("td")
            var usedCell = document.createElement("td")
            tr.appendChild(keyCell)
            tr.appendChild(usedCell)
            table.appendChild(tr)
        } else {
            var tr = rows[i]
            var keyCell = tr.children[0]
            var usedCell = tr.children[1]
        }

        keyCell.innerHTML = state.apiKeys[i][0]
        usedCell.innerHTML = state.apiKeys[i][1]
    }
}


function updateStateNumbers() {
    
}


async function main() {
    const adminState = await JSON.parse(await (await fetch(`/admin-view/${apiKey}`)).text())
    updateAPIKeyTable(adminState)
}


window.onload = () => {
    stateNumbersDiv = document.getElementById("state-numbers")

    window.setInterval(main, 500)
}