//#### TODOS ####
btn_cambiar_contrase_staff=document.getElementById("btn_cambiar_contrase_staff")
if(btn_cambiar_contrase_staff){
    btn_cambiar_contrase_staff.addEventListener('click',function(e){
        document.getElementById("form_cambiar_contraseña").submit()
    })
}
let btn_get_cerrar_sesion = document.getElementById("btn_get_cerrar_sesion")
if(btn_get_cerrar_sesion){
    btn_get_cerrar_sesion.addEventListener('click',function(e){
        document.getElementById("opc_nav").value="cerrar_sesion"
        document.getElementById("form_nav").submit()
    })
}


//#### AMDIN ####
let btn_get_aniadir_producto_almacen = document.getElementById("btn_get_aniadir_producto_almacen")
if(btn_get_aniadir_producto_almacen){
    btn_get_aniadir_producto_almacen.addEventListener('click',function(e){
        document.getElementById("opc_sidebar").value="get_aniadir_producto_almacen"
        document.getElementById("form_sidebar").submit()
    })
}

let btn_get_inventario_mostrador = document.getElementById("btn_get_inventario_mostrador")
if(btn_get_inventario_mostrador){
    btn_get_inventario_mostrador.addEventListener('click',function(e){
        document.getElementById("opc_sidebar").value="get_inventario_mostrador"
        document.getElementById("form_sidebar").submit()
    })
}

let btn_get_inventario_almacen = document.getElementById("btn_get_inventario_almacen")
if(btn_get_inventario_almacen){
    btn_get_inventario_almacen.addEventListener('click',function(e){
        document.getElementById("opc_sidebar").value="get_inventario_almacen"
        document.getElementById("form_sidebar").submit()
    })
}




let otra_categoria = document.getElementById("categoria")
if(otra_categoria){
    otra_categoria.addEventListener('change',function(e){
        if(e.target.value=="otra"){
            var inputOtraCategoria = document.getElementById("otra_categoria");
            inputOtraCategoria.classList.remove("d-none");
        }else{
            var inputOtraCategoria = document.getElementById("otra_categoria");
            inputOtraCategoria.classList.add("d-none");
        }
    })
    if(otra_categoria.value=="otra"){
        var inputOtraCategoria = document.getElementById("otra_categoria");
        inputOtraCategoria.classList.remove("d-none");
    }else{
        var inputOtraCategoria = document.getElementById("otra_categoria");
        inputOtraCategoria.classList.add("d-none");
    }
}

let btn_get_empleados = document.getElementById("btn_get_empleados")
if(btn_get_empleados){
    btn_get_empleados.addEventListener('click',function(e){
        document.getElementById("opc_sidebar").value="get_empleados"
        document.getElementById("form_sidebar").submit()
    })
}

let btn_cancelar_modificar_empleado = document.getElementById("btn_cancelar_modificar_empleado");
if (btn_cancelar_modificar_empleado) { // Verifica si hay elementos
    btn_cancelar_modificar_empleado.addEventListener('click', function(e) {
        document.getElementById("opc_sidebar").value="get_empleados"
        document.getElementById("form_sidebar").submit()
    });
};











let btn_get_informe = document.getElementById("btn_get_informe")
if(btn_get_informe){
    btn_get_informe.addEventListener('click',function(e){
        document.getElementById("opc_sidebar").value="get_informe"
        document.getElementById("form_sidebar").submit()
    })
}


let registrar_empleado = document.getElementById("registrar_empleado")
if(registrar_empleado){
    registrar_empleado.addEventListener('click',function(e){
        document.getElementById("form_registrar_empleado").submit()
    })
}
let btn_get_carrito = document.getElementById("btn_get_carrito")
if(btn_get_carrito){
    btn_get_carrito.addEventListener('click',function(e){
        document.getElementById("opc_nav").value="get_carrito"
        document.getElementById("form_nav").submit()
    })
}
let btn_get_compras = document.getElementById("btn_get_compras")
if(btn_get_compras){
    btn_get_compras.addEventListener('click',function(e){
        document.getElementById("opc_nav").value="get_compras"
        document.getElementById("form_nav").submit()
    })
}
let btn_get_pefil = document.getElementById("btn_get_pefil")
if(btn_get_pefil){
    btn_get_pefil.addEventListener('click',function(e){
        document.getElementById("opc_nav").value="get_pefil"
        document.getElementById("form_nav").submit()
    })
}


//#### CLIENTE ####
let btn_login_client=document.getElementById("btn_login_client")
if(btn_login_client){
    btn_login_client.addEventListener('click',function(e){
        document.getElementById("form_iniciar_sesion_client").submit()
    })
}

