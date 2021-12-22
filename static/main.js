var contentDiv
var apiKeyEnterDiv

var followerCountP
var readyCountP
var feedTable
var beliefStateInputDiv
var apiKey = ""

var hasSetUpBeliefStateInputDiv = false
var hasSetUpFeedTableRows = false

var step = 0


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

    hasSetUpBeliefStateInputDiv = true
}


function setUpFeedTableRows(count) {
    const cols = ["User", "Latest Post", "Followers", "Unfollow"]

    for (let i = 0; i < count + 1; i++) {
        let row = document.createElement("tr")
        row.id = `feed_row_${i}`

        let cellType = "td"
        if (i == 0) cellType = "th"
        
        for (let c = 0; c < cols.length; c++) {
            let cell = document.createElement(cellType)
            if (i > 0) {
                cell.id = `feed_row_${i}_${cols[c]}`

                if (cols[c] == "Unfollow") {
                    let unfollowBox = document.createElement("input")
                    unfollowBox.type = "checkbox"
                    unfollowBox.id = `unfollow_checkbox_${c}`
                    cell.appendChild(unfollowBox)
                }
                else cell.innerText = "___"
            }
            else cell.innerText = cols[c]
            row.appendChild(cell)
        }
        feedTable.appendChild(row)
    }

    hasSetUpFeedTableRows = true
}


function getFeedTableCell(col, row) {
    console.log(`feed_row_${row}_${col}`)
    return document.getElementById(`feed_row_${row}_${col}`)
}


function getMessage() {
    const message = []
    let children = beliefStateInputDiv.children
    for (let i = 0; i < children.length; i++) {
        message.push(parseInt(children[i].value))
    }
    return message
}


function getIssueStringFromInts(issues, ints) {
    let str = ""
    for (let i = 0; i < issues.length; i++) {
        if (ints[i] == -1) str += String(issues[i][0])
        else str += String(issues[i][1])
        str += "\t"
    }
    return str
}


function fillMessageTable(messages, issues) {
    // messages is an array of message dictionaries
    for (let i = 0; i < messages.length; i++) {
        let c = i + 1
        let message = messages[i]
        getFeedTableCell("User", c).innerText = message["User"]
        getFeedTableCell("Latest Post", c).innerText = getIssueStringFromInts(issues, 
            message["Latest Post"])
        getFeedTableCell("Followers", c).innerText = message["Followers"]
    }
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
    }
}


function setAPIKey() {
    apiKey = document.getElementById("api-key-input-box").value
}


async function update() {
    const state = await JSON.parse(await (await fetch(`/state/${apiKey}`)).text())

    if (state.team != null) {
        let teamP = document.getElementById("team")
        teamP.innerText = state.team[0]
        teamP.style.color = state.team[1]
        teamP.hidden = false
    }

    if (!hasSetUpBeliefStateInputDiv) setUpBeliefStateInputDiv(state.issues)
    if (!hasSetUpFeedTableRows) setUpFeedTableRows(state.outDegree)

    if (state.step != step) {
        step = state.step
        document.getElementById("ready").checked = false
    }

    checkReady()

    followerCountP.innerHTML = `You have ${state.followers} followers!`
    readyCountP.innerHTML = `${state.readyCount} of ${state.size} people are ready!`

    if (state.messages.length > 0) fillMessageTable(state.messages, state.issues)
}


async function main() {
    if (apiKey != "") {
        contentDiv.hidden = false
        apiKeyEnterDiv.hidden = true
        update()
    }
}


window.onload = () => {
    contentDiv = document.getElementById("content")
    apiKeyEnterDiv = document.getElementById("api-key-input")

    followerCountP = document.getElementById("follower-count")
    readyCountP = document.getElementById("ready-count")
    feedTable = document.getElementById("feed")
    beliefStateInputDiv = document.getElementById("belief-state-expression")

    document.getElementById("team").hidden = true
    document.getElementById("ready").checked = false

    contentDiv.hidden = true

    window.setInterval(main, 500)
}