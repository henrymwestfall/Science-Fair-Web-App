var form
const inputElements = []
const dataToInputTypes = {
    "string": "text",
    "number": "text",
    "boolean": "checkbox"
}


function createFormData() {
    // create data object to send with correct data types
    let params = {}
    for (child of inputElements) {
        let numParse = parseFloat(child.value)
        if (isNaN(numParse)) // the value is not a number, so store the string
            params[child.name] = child.value
        else // the value is a number, so store it in the data as such
            params[child.name] = numParse
    }

    return params
}


function submitForm() {
    let params = createFormData()

    let data = new FormData()
    data.append("data", JSON.stringify(params))

    fetch(`/create-simulation/${apiKey}`, {
        method: "POST",
        body: data
    }).then(response => {
        response.text().then(text => {
            const error = JSON.parse(text).error
            if (error != null) alert(error)
            else alert("Successfully created a new simulation!")
        })
    })
}


window.onload = () => {
    form = document.getElementById("setup-form")

    fetch(`/get-default-parameters/${apiKey}`).then(response => {
        response.text().then(text => {
            const defaultParameters = JSON.parse(text)
            const error = defaultParameters.error
            if (error != null) alert(error)

            // create form from default parameters
            for (const [param, defaultValue] of Object.entries(defaultParameters)) {
                // first, create a label for the parameter
                let label = document.createElement("label")
                label.for = param
                label.innerText = `${param}: `
                form.appendChild(label)
                
                // then, create an input element of the correct type
                let inputElement = document.createElement("input")
                inputElement.type = dataToInputTypes[typeof(defaultValue)]
                inputElement.name = param
                inputElement.value = defaultValue
                form.appendChild(inputElement)
                inputElements.push(inputElement)

                // add a break between this and the next input
                form.appendChild(document.createElement("br"))
            }
        })
    })
}