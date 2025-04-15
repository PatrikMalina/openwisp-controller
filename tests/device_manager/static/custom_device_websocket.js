"use strict";
/* global console */  // Tell JSHint that `console` is available

document.addEventListener("DOMContentLoaded", function () {
    const socket = new WebSocket(`ws://${window.location.host}/ws/device/?id=0&key=0`);

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

            // case "device_metrics":
            //     updateDeviceMetrics(message.data)
            //     break

            default:
                console.log('Received WebSocket command: ', message.command);

        }
    };

    socket.onopen = function () {
        console.log("WebSocket connected.");
    };

    socket.onerror = function (error) {
        console.error("WebSocket Error: ", error);
    };

    socket.onclose = function () {
        console.log("WebSocket connection closed.");
    };
});
