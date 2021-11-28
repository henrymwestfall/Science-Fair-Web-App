var score_div;
var feed_table;
var belief_expression;


function createIssueExpressionElement(issue) {
    console.log(issue)
    let e = document.createElement("span")
    e.innerText = issue
    belief_expression.appendChild(e)
}


async function main() {
    const state = await JSON.parse(await (await fetch(`/state/${apiKey}`)).text())

    // create elements for inputting issues
    if (belief_expression.children.length == 0) {
        for (let i = 0; i < state.issues.length; i++) {
            createIssueExpressionElement(state.issues[i])
        }
    }
}


window.onload = () => {
    score_div = document.getElementById("score")
    feed_table = document.getElementById("feed")
    belief_expression = document.getElementById("belief-state-expression")

    // window.setInterval(main, 250)
    main()
}