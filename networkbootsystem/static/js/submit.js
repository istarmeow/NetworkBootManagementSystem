

function delete_confirmation() {
    if (!confirm("确认删除？")) {
    window.event.returnValue = false;
    }
    }


function operation_confirmation() {
    if (!confirm("确认操作？")) {
        window.event.returnValue = false;
    }
}

//模态框删除确认提交
function delcfm(url) {
      $('#url').val(url);//给会话中的隐藏属性URL赋值
      $('#delcfmModel').modal();
}
function urlSubmit(){
   var url=$.trim($("#url").val());//获取会话中的隐藏属性URL
   window.location.href=url;
}




//用户登录提示
$('#username').blur(function(){
    var input_username = $(this).val();
    $.ajax({
        url: "/user/login",
        date: {username: input_username},
        type: "POST",
        success: function(arg){
            alert(arg)
        }
    });
});

//验证需要做url的输入不能包含某些特殊字符
function TextVerifyInput(str){
//    alert(str);
    var re=/[+/?%#&=]+/;
    var mt = re.exec(str)

    if(mt){
        mt = "不能出现“" + mt + "”符号！"
        alert(mt);
        return false;
    }
    else{
//        alert('通过');
    }
}

//判断输入的盘符是不是单个英文字母
function TextVerifyDsik(str){
//    alert(str);
    var re=/^[g-zG-Z]$/;
    var mt = re.exec(str)

    if(!mt){
        mt = "只能是g-z的单个英文字母！"
        alert(mt);
        return false;
    }
    else{
//        alert('通过');
    }
}
