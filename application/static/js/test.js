

// Event
document.getElementById("button-js").addEventListener("click", function(){
    navigator.clipboard.readText()
    .then(text => {
      console.log('Pasted content: ', text);
      document.getElementById("button-js").value = text;
    })
    .catch(err => {
      console.error('Failed to read clipboard contents: ', err);
    });
    });
