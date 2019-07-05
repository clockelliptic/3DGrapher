import QtQuick 2.10
import QtQuick.Controls 2.1
import QtQuick.Window 2.2
import QtQuick.Layouts 1.8
import QtQuick.Controls.Material 2.3

ApplicationWindow {
    id: applicationWindow
    Material.theme: Material.Dark
    title: qsTr("Test Invoke")
    visible: true

    width: 720;
    height: 480;

    GridLayout{
        width: parent.width;
        anchors.centerIn: parent;
        anchors.fill: parent;
        flow:  width > 320 ? GridLayout.LeftToRight : GridLayout.TopToBottom;
        columnSpacing: 10;
        rowSpacing: 10;
        columns: parseInt(parent.width / 160)

        id: mainGrid

        Rectangle {
            id: rect0;
            color: "transparent";
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            implicitWidth: 160;
            implicitHeight: 160;

            Rectangle {
                width: parent.width > parent.height ? parent.height : parent.width
                height: parent.width > parent.height ? parent.height : parent.width
                color: "#ffffff"
                anchors.centerIn: parent
            }
        }
        Rectangle {
            id: rect1;
            color: "transparent";
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            implicitWidth: 160;
            implicitHeight: 160;
            Rectangle {
                width: parent.width > parent.height ? parent.height : parent.width
                height: parent.width > parent.height ? parent.height : parent.width
                color: "#ffffff"
                anchors.centerIn: parent
            }
        }
        Rectangle {
            id: rect2;
            color: "transparent";
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            implicitWidth: 160;
            implicitHeight: 160;
            Rectangle {
                width: parent.width > parent.height ? parent.height : parent.width
                height: parent.width > parent.height ? parent.height : parent.width
                color: "#ffffff"
                anchors.centerIn: parent
            }
        }
        Rectangle {
            id: rect3;
            color: "transparent";
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            implicitWidth: 160;
            implicitHeight: 160;
            Rectangle {
                width: parent.width > parent.height ? parent.height : parent.width
                height: parent.width > parent.height ? parent.height : parent.width
                color: "#ffffff"
                anchors.centerIn: parent
            }
        }
        Rectangle {
            id: rect4;
            color: "transparent";
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            implicitWidth: 160;
            implicitHeight: 160;
            Rectangle {
                width: parent.width > parent.height ? parent.height : parent.width
                height: parent.width > parent.height ? parent.height : parent.width
                color: "#ffffff"
                anchors.centerIn: parent
            }
        }
        Rectangle {
            id: rect5;
            color: "transparent";
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            implicitWidth: 160;
            implicitHeight: 160;
            Rectangle {
                width: parent.width > parent.height ? parent.height : parent.width
                height: parent.width > parent.height ? parent.height : parent.width
                color: "#ffffff"
                anchors.centerIn: parent
            }

        }
    }

}