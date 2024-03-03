document.getElementById("submit-button").addEventListener("click", function () {
    document.getElementById("processing").style.display = "block";
});

// jQueryを使用している場合
$(document).ready(function() {
    // 初期状態では非表示にする
    $(".display-text").hide();

    // ボタンがクリックされたときの処理
    $("#toggleButton").click(function() {
        // .toggle()メソッドを使用して表示と非表示を切り替える
        $(".display-text").toggle();
    });
});

// jQueryを使用していない場合
// document.addEventListener("DOMContentLoaded", function() {
//     // 初期状態では非表示にする
//     var displayText = document.querySelector(".display-text");
//     displayText.style.display = "none";

//     // ボタンがクリックされたときの処理
//     var toggleButton = document.getElementById("toggleButton");
//     toggleButton.addEventListener("click", function() {
//         // style.displayプロパティを使用して表示と非表示を切り替える
//         if (displayText.style.display === "none") {
//             displayText.style.display = "block";
//         } else {
//             displayText.style.display = "none";
//         }
//     });
// });