// 註冊框框
$('#register').on('click', function () {
    $("#registWindow").modal("toggle");
})

// 登入框框
$('#login').on('click', function () {
    console.log("login")
    $("#loginWindow").modal("toggle");
})

// 註冊完成
$('#doneRegisting').on('click', regist);
$('#registWindow').on('keypress',function(e){
    if(e.which == 13){
        regist();
    }
})

function regist() {
    var mName = $("#mName").val();
    var mEmail = $("#mEmail").val();
    var mPw = $("#mPw").val();
    var mCity = $("select[name='county']").val();
    var mRegion = $("select[name='district']").val();
    var mAddress = $("#street").val();
    if (mName != "" && mEmail != "" && mPw != "" && mCity != "" && mRegion != "" && mAddress != "") {
        $.ajax({
            method: "POST",
            url: "/api/users/regist",
            data: {
                mName:mName,
                mEmail:mEmail,
                mPw:mPw,
                mCity:mCity,
                mRegion:mRegion,
                mAddress:mAddress
            },
            success: function(msg) {
                if (msg.status) {
                    window.location.href = "/";
                } else {
                    window.location.reload();
                }
            }
        })
    }
}

// 登入完成
$('#doneLogin').on('click', login)
$('#loginWindow').on('keypress',function(e){
    if(e.which == 13){
        login();
    }
})

function login(){
    var account = $("#account").val();
    var psw = $("#psw").val();
    if (account != "" && psw != "") {
        $.ajax({
            method: "POST",
            url: "/api/users/login",
            data: {
                account:account,
                psw:psw,
            },
            success: function(msg) {
                if (msg.status) {
                    window.location.href = "/plan";
                } else {
                    window.location.reload();
                }
            }
        })
    }
}