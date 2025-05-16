"use strict";
/* global console */  // Tell JSHint that `console` is available

document.addEventListener("DOMContentLoaded", function () {
    const isDetailPage = window.location.href.includes("/change/");
    const socket = new WebSocket(`ws://${window.location.host}/ws/webclient/`);

    let deviceId = null;

    const metricLabels = {
        cpu_load: "CPU Load (%)",
        memory_usage: "Memory Usage (%)",
        disk_read: "Disk Read (MB/s)",
        disk_write: "Disk Write (MB/s)",
        bytes_sent: "Network Sent (KB/s)",
        bytes_recv: "Network Received (KB/s)"
    };
    const charts = {};

    const style = document.createElement("style");
    style.innerHTML = `
        #device-metrics-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
    
        .chart-wrapper {
            flex: 0 0 30%;
            background: #f9f9f9;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        `;
    document.head.appendChild(style);

    const container = document.createElement("div");
    container.id = "device-metrics-container";
    container.style.marginTop = "30px";

    if (isDetailPage) {
        deviceId = document.querySelector(".form-row.field-id .readonly").textContent.trim();

        const buttonRow = document.querySelector(".submit-row");
        if (buttonRow) {
            buttonRow.insertAdjacentElement("afterend", container);
        } else {
            document.body.appendChild(container);
        }

        const logWrapper = document.createElement("div");
        logWrapper.className = "chart-wrapper";
        logWrapper.style.flex = "1 1 100%";
        logWrapper.innerHTML = `
            <h4 style="margin-bottom: 5px;">Script Output</h4>
            <textarea id="script-log" style="width: 100%; height: 200px; font-family: monospace;" readonly></textarea>
        `;
        container.appendChild(logWrapper);
    }


    function createChart(metric) {
        const canvasId = `chart-${metric}`;

        const wrapper = document.createElement("div");
        wrapper.className = "chart-wrapper";
        wrapper.innerHTML = `
        <h4 style="margin-bottom: 5px;">${metricLabels[metric]}</h4>
        <canvas id="${canvasId}" height="100"></canvas>
    `;

        container.appendChild(wrapper);

        const ctx = document.getElementById(canvasId).getContext("2d");

        charts[metric] = new Chart(ctx, {
            type: "line",
            data: {
                labels: [],
                datasets: [{
                    label: metricLabels[metric],
                    data: [],
                    borderWidth: 2,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                animation: false,
                scales: {
                    x: {ticks: {autoSkip: true, maxTicksLimit: 10}},
                    y: {beginAtZero: true}
                }
            }
        });
    }

    function updateChart(metric, value) {
        if (!charts[metric]) {
            createChart(metric);
        }

        const chart = charts[metric];
        const now = new Date().toLocaleTimeString();

        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(value);

        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update();
    }

    function updateDeviceStatus(data) {
        const rows = document.querySelectorAll("#result_list tbody tr");

        const isConnected = data.status.toLowerCase() === "connected";

        rows.forEach(function (row) {
            const idCell = row.querySelector(".field-id");  // Select ID column
            if (idCell && idCell.textContent.trim() === String(data.id)) {
                const statusCell = row.querySelector(".field-status");  // Select status column
                if (statusCell) {
                    statusCell.innerHTML = `<span style="color: ${isConnected ? "green" : "red"}; font-weight: bold;">
                                                ${isConnected ? "Connected" : "Disconnected"}
                                            </span>`;
                }
            }
        });
    }

    function loadInitialStatus(data) {
        data.forEach(device => updateDeviceStatus(device));
    }

    socket.onmessage = function (event) {
        const message = JSON.parse(event.data);

        switch (message.command) {
            case "status":
                updateDeviceStatus(message.data);
                break;
            case "connected_devices":
                loadInitialStatus(message.data);
                break;
            case "new_device":
                location.reload();
                break;

            case "metrics":
                if (message.data.id === deviceId) {
                    const metrics = message.data;

                    Object.keys(metricLabels).forEach(metric => {
                        if (metrics[metric] !== undefined) {
                            updateChart(metric, metrics[metric]);
                        }
                    });
                }
                break

            case "script_log":
                const logBox = document.getElementById("script-log");
                if (logBox) {
                    if (message.data.full) {
                        logBox.value = message.data.text
                    } else {
                        logBox.value += `${message.data}\n`;
                    }
                }
                break;

            default:
                console.log(`Received WebSocket command:${message.command}`);

        }
    };

    socket.onopen = function () {
        console.log("WebSocket connected.");

        if (isDetailPage && deviceId) {
            socket.send(JSON.stringify({
                command: "script_log",
                data: deviceId
            }));
        }
    };

    socket.onerror = function (error) {
        console.error("WebSocket Error: ", error);
    };

    socket.onclose = function () {
        console.log("WebSocket connection closed.");
    };
});
