var contentDiv
var apiKeyEnterDiv

var likesCountP
var timeAndReadyP
var feedTable
var beliefStateInputDiv

var apiKey = ""

var hasSetUpBeliefStateInputDiv = false
var hasSetUpFeedTableRows = false

var step = 0

var follows = []


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
    const recommend = "Keep recommending user"
    const reject = "Stop recommending user"
    const cols = ["Latest Post", "Views", "User", recommend, reject]

    for (let i = 0; i < count + 1; i++) {
        let row = document.createElement("tr")
        row.id = `feed_row_${i}`

        let cellType = "td"
        if (i == 0) cellType = "th"
        
        for (let c = 0; c < cols.length; c++) {
            let cell = document.createElement(cellType)
            if (i > 0) {
                cell.id = `feed_row_${i}_${cols[c]}`

                if (cols[c] == reject) {
                    let unfollowBox = document.createElement("input")
                    unfollowBox.addEventListener("change", (_) => {
                        handleActionCheckboxChange("unfollow", i)
                    })
                    unfollowBox.type = "checkbox"
                    unfollowBox.id = `unfollow_checkbox_${i}`
                    cell.appendChild(unfollowBox)
                } else if (cols[c] == recommend) {
                    let followBox = document.createElement("input")
                    followBox.addEventListener("change", (_) => {
                        handleActionCheckboxChange("follow", i)
                    })
                    followBox.type = "checkbox"
                    followBox.id = `follow_checkbox_${i}`
                    cell.appendChild(followBox)
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


function handleActionCheckboxChange(checkboxType, i) {
    let checkboxID = `${checkboxType}_checkbox_${i}`
    let otherID = (checkboxType == "follow" ? 
        `unfollow_checkbox_${i}` : `follow_checkbox_${i}`)
    let checkbox = document.getElementById(checkboxID)
    let otherbox = document.getElementById(otherID)
    if (checkbox.checked) {
        otherbox.checked = false
    }

    if (document.getElementById(`follow_checkbox_${i}`).checked) {
        follows[i - 1] = 1
    } else if (document.getElementById(`unfollow_checkbox_${i}`).checked) {
        follows[i - 1] = -1
    } else {
        follows[i - 1] = 0
    }
}


function getFeedTableCell(col, row) {
    return document.getElementById(`feed_row_${row}_${col}`)
}


function getMessage() {
    const message = []
    let children = beliefStateInputDiv.children
    for (let i = 1; i < children.length; i++) {
        message.push(parseInt(children[i].value))
    }
    return message
}


// function getUnfollows() {
//     let unfollows = []
//     for (let i = 1; i < feedTable.children; i++) {
//         let unfollowCheckbox = document.getElementById(`unfollow_checkbox_${i}`)
//         let influencerNameElement = document.getElementById(`feed_row_${i}_User`)
//         let influencerName = influencerNameElement.innerText
//         if (unfollowCheckbox.checked) unfollows.push(influencerName)
//     }

//     return unfollows
// }


// function getFollows() {
//     let follows = []
//     for (let i = 1; i < feedTable.children; i++) {
//         let followCheckbox = document.getElementById(`follow_checkbox_${i}`)
//         let influencerNameElement = document.getElementById(`feed_row_${i}_User`)
//         let influencerName = influencerNameElement.innerText
//         if (followCheckbox.checked) follows.push(influencerName)
//     }

//     return follows
// }


function uncheckAllUnfollowCheckboxes() {
    for (let i = 1; i < feedTable.children.length; i++) {
        document.getElementById(`unfollow_checkbox_${i}`).checked = false
        document.getElementById(`follow_checkbox_${i}`).checked = false
        follows = Array.from({length: follows.length}, (v, i) => 0)
    }
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
        getFeedTableCell("Views", c).innerText = message["Views"]
    }
}


function checkReady() {
    let readyElem = document.getElementById("ready")
    if (readyElem.checked) {
        let data = new FormData()
        data.append("data", JSON.stringify({
            "message": getMessage(),
            "follows": follows
        }))

        fetch(`/send-actions/${apiKey}`, {
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

    if (follows.length == 0) {
        follows = Array.from({length: state.outDegree}, (v, i) => 0)
    }

    if (!hasSetUpBeliefStateInputDiv) setUpBeliefStateInputDiv(state.issues)
    if (!hasSetUpFeedTableRows) setUpFeedTableRows(state.outDegree)

    if (state.step != step) {
        document.getElementById("step").innerHTML = `Round ${state.step}`
        step = state.step
        document.getElementById("ready").checked = false
        uncheckAllUnfollowCheckboxes()
    }

    checkReady()

    let secondsLeft = Math.floor(state.stepEndTime - (new Date()).getTime() / 1000)
    if (secondsLeft < 0) secondsLeft = 0

    let secondsOnTime = secondsLeft % 60
    let minutesLeft = (secondsLeft - secondsOnTime) / 60

    let timeStr = ""
    if (secondsOnTime < 10) {
        timeStr = `${minutesLeft}:0${secondsOnTime}`
    } else {
        timeStr = `${minutesLeft}:${secondsOnTime}`
    }

    likesCountP.innerHTML = `You've gotten ${state.likes} total likes! (+${state.likeChange} last round)`
    timeAndReadyP.innerHTML = `${timeStr} remaining in this round!
                                ${state.readyCount} of ${state.size} people are waiting for you.`

    if (state.messages.length > 0) fillMessageTable(state.messages, state.issues)
}


async function main() {
    if (apiKey != "") {
        contentDiv.hidden = false
        apiKeyEnterDiv.remove()
        update()
    }
}


window.onload = () => {
    contentDiv = document.getElementById("content")
    apiKeyEnterDiv = document.getElementById("api-key-input")

    likesCountP = document.getElementById("likes-count")
    timeAndReadyP = document.getElementById("time-and-ready")
    feedTable = document.getElementById("feed")
    beliefStateInputDiv = document.getElementById("belief-state-expression")

    document.getElementById("ready").checked = false

    contentDiv.hidden = true

    window.setInterval(main, 500)
}