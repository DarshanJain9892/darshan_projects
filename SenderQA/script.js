// Sample data for the table
const tableData = [
    { srNo: 1, appName: "SMSSenderReceiver", ui: "SR_URLs" },
    { srNo: 2, appName: "SMSSenderDispatcher", ui: "DISP_URLs" },
    { srNo: 3, appName: "SMSSenderCallBack", ui: "SMSCB_URLs" },
    { srNo: 4, appName: "SMSSenderSupport", ui: "SUPPORT_URLs" },
    { srNo: 5, appName: "SenderManagement", ui: "MANAGEMENT_URLs" },
    { srNo: 6, appName: "HTTPSender", ui: "HTTPSENDER_URLs" },
    { srNo: 7, appName: "WABAManager", ui: "WM_URLs" },
    { srNo: 8, appName: "DataReceiver", ui: "DR_URLs" },
    { srNo: 9, appName: "DynamicQueueManager", ui: "DQM_URLs" },
    { srNo: 10, appName: "DataHttpSender", ui: "DHS_URLs" },
    { srNo: 11, appName: "SMPPSender", ui: "SMPP_URLs" },
    { srNo: 12, appName: "SMPPSenderCallBack", ui: "SMPPCB_URLs" }
];

// Function to populate the table
function populateTable(data) {
    const tableBody = document.querySelector("#appTable tbody");
    tableBody.innerHTML = ""; // Clear existing rows
    data.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.srNo}</td>
            <td><a href="${row.appName.toLowerCase()}.html">${row.appName}</a></td>
            <td><a href="${row.ui.toLowerCase()}.html">${row.ui}</a></td>
        `;
        tableBody.appendChild(tr);
    });
}

// Initialize the table with data
populateTable(tableData);
