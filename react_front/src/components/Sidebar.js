import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import './Sidebar.css'
import logo from "./resources/logo.png"

const Sidebar = () => {
  return(
     <div className={"sidebar"}>
         <img src={logo}/>
         <li>
             Исходные данные
         </li>
         <li>
             Оптимизация
         </li>
     </div>
  )
}

export default Sidebar