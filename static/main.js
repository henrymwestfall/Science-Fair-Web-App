var scoreDiv
var feedTable
var beliefStateInputDiv
var apiKey = ""


function setUpBeliefStateInputDiv(issues) {
    for (let i = 0; i < issues.length; i++) {
        let select = document.createElement("select")
        select.id = `issue_${i}`
        select.classList.add("issue")
        select.name = select.id

        let optionElements = []

        for (let opt = 0; opt < 2; opt++) {
            let option = document.createElement("option")
            option.value = opt == 0 ? -1 : 1
            option.innerText = issues[i][opt]
            optionElements.push(option)
        }

        // shuffle to avoid any bias
        optionElements = optionElements.sort(() => Math.random() - 0.5)
        for (let opt = 0; opt < optionElements.length; opt++) {
            select.appendChild(optionElements[opt])
        }

        beliefStateInputDiv.appendChild(select)
    }
}


function setUpFeedTableRows(count) {
    const cols = ["User", "Latest Post", "Followers"]

    for (let i = 0; i < count + 1; i++) {
        let row = document.createElement("tr")
        row.id = `feed_row_${i}`

        let cellType = "td"
        if (i == 0) cellType = "th"
        
        for (let c = 0; c < 3; c++) {
            let cell = document.createElement(cellType)
            if (i > 0) {
                cell.id = `feed_row_${i}_${cols[c]}`
                cell.innerText = "___"
            }
            else cell.innerText = cols[c]
            row.appendChild(cell)
        }
        feedTable.appendChild(row)
    }
}


function getMessage() {
    const message = []
    let children = beliefStateInputDiv.children
    for (let i = 0; i < children.length; i++) {
        message.push(parseInt(children[i].value))
    }
    return message
}


function checkReady() {
    let readyElem = document.getElementById("ready")
    if (readyElem.checked) {
        let data = new FormData()
        data.append("data", JSON.stringify({"message": getMessage()}))

        fetch(`/send-message/${apiKey}`, {
            method: "POST",
            body: data
        }).then((response) => {
            response.text().then((text) => {
                const error = JSON.parse(text).error
                if (error != null) alert(error)
            })
        })

        readyElem.checked = false
    }
}


function clearAPIkey() {
    apiKey = ""
}


async function update() {
    const state = await JSON.parse(await (await fetch(`/state/${apiKey}`)).text())

    if (state.error == "keyNotFound") {
        clearAPIkey()
        return
    }

    if (beliefStateInputDiv.children.length == 0) setUpBeliefStateInputDiv(state.issues)
    if (feedTable.children.length == 0) setUpFeedTableRows(state.outDegree)

    checkReady()

    if (state.messages.length > 0) alert ("FINALLY GODDAMMIT")
}


async function main() {
    if (apiKey == "") {
        const resp = await JSON.parse(await (await fetch(`/new-apikey`)).text())
        apiKey = resp.apiKey
        document.cookie = apiKey
    } else {
        update()
    }
}


window.onload = () => {
    apiKey = document.cookie

    scoreDiv = document.getElementById("score")
    feedTable = document.getElementById("feed")
    beliefStateInputDiv = document.getElementById("belief-state-expression")

    document.getElementById("ready").checked = false
    window.setInterval(main, 500)
}