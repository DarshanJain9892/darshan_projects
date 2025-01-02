// Utility functions for conversions
function hexToString(hex) {
    try {
      return decodeURIComponent(
        hex.replace(/../g, (byte) => `%${byte}`)
      );
    } catch {
      return "Invalid Hex Input";
    }
  }
  
  function stringToHex(str) {
    return Array.from(str)
      .map((char) => char.charCodeAt(0).toString(16).padStart(2, "0"))
      .join("");
  }
  
  function urlEncode(str) {
    return encodeURIComponent(str);
  }
  
  function urlDecode(str) {
    try {
      return decodeURIComponent(str);
    } catch {
      return "Invalid URL Input";
    }
  }
  
  async function stringToHash(str) {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  
  async function convert(action) {
    const input = document.getElementById("input").value;
    const outputElement = document.getElementById("output");
    
    switch (action) {
      case "hexToString":
        outputElement.textContent = hexToString(input);
        break;
      case "stringToHex":
        outputElement.textContent = stringToHex(input);
        break;
      case "urlEncode":
        outputElement.textContent = urlEncode(input);
        break;
      case "urlDecode":
        outputElement.textContent = urlDecode(input);
        break;
      case "stringToHash":
        outputElement.textContent = await stringToHash(input);
        break;
      default:
        outputElement.textContent = "Unknown action.";
    }
  }
  function copyToClipboard() {
    const output = document.getElementById('output').innerText;
    if (output) {
        navigator.clipboard.writeText(output).then(() => {
            alert('Output copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    } else {
        alert('Nothing to copy!');
    }
}  