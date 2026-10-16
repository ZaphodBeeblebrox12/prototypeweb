/* Shared instructional-image replacement hook for server-authorised editors. */
(() => {
 "use strict";
 const config=window.TRADETHESIS_MEDIA_EDITOR;
 // Static previews have no auth context or upload backend; never show fake controls.
 if(!config||config.enabled!==true||!config.csrfToken)return;
 const maxBytes=Number(config.maxBytes)>0?Number(config.maxBytes):10*1024*1024;
 const allowedTypes=new Set(["image/jpeg","image/png","image/webp"]),attached=new WeakSet();
 function status(node,message,error){node.textContent=message;node.dataset.state=error?"error":"info";}
 function attach(img){
  if(!(img instanceof HTMLImageElement)||attached.has(img)||!img.dataset.mediaAssetId||!img.dataset.mediaReplaceUrl)return;
  attached.add(img);const figure=img.closest("figure")||img.parentElement;if(!figure)return;
  const bar=document.createElement("div");bar.className="tt-media-replace-control";
  const btn=document.createElement("button");btn.type="button";btn.className="tt-media-replace-button";btn.textContent="Replace image";btn.setAttribute("aria-label","Replace this course image");
  const msg=document.createElement("span");msg.className="tt-media-replace-status";msg.setAttribute("role","status");msg.setAttribute("aria-live","polite");
  const input=document.createElement("input");input.type="file";input.accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp";input.hidden=true;input.tabIndex=-1;
  bar.append(btn,msg,input);const action=figure.querySelector(".course-reference-actions");if(action)action.append(bar);else img.insertAdjacentElement("afterend",bar);
  btn.addEventListener("click",()=>{if(!btn.disabled)input.click();});
  input.addEventListener("change",async()=>{
   const file=input.files&&input.files[0];if(!file)return;
   if(!allowedTypes.has(file.type)){status(msg,"Choose a JPG, PNG or WebP image.",true);input.value="";return;}
   if(file.size<=0||file.size>maxBytes){status(msg,"The image must be smaller than "+Math.round(maxBytes/1048576)+" MB.",true);input.value="";return;}
   btn.disabled=true;status(msg,"Uploading image…",false);const data=new FormData();data.append("image",file,file.name);data.append("asset_id",img.dataset.mediaAssetId);
   try{
    const response=await fetch(img.dataset.mediaReplaceUrl,{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":config.csrfToken,"Accept":"application/json"},body:data});
    let result={};try{result=await response.json();}catch(_){}
    if(!response.ok||result.ok!==true||typeof result.image_url!=="string")throw new Error(result.detail||"The image could not be replaced. Try again.");
    const url=new URL(result.image_url,window.location.href);if(!["http:","https:"].includes(url.protocol))throw new Error("The server returned an invalid image URL.");
    const id=img.dataset.mediaAssetId;
    document.querySelectorAll("img[data-media-asset-id]").forEach(target=>{if(target.dataset.mediaAssetId!==id)return;target.src=url.href;target.removeAttribute("srcset");if(typeof result.alt==="string")target.alt=result.alt;});
    status(msg,"Image replaced. The shared image is updated.",false);
    document.dispatchEvent(new CustomEvent("tradethesis:media-replaced",{detail:{assetId:id,imageUrl:url.href}}));
   }catch(err){status(msg,err&&err.message?err.message:"Upload failed. Please try again.",true);}
   finally{btn.disabled=false;input.value="";}
  });
 }
 function scan(root){if(!root||!(root instanceof Element||root instanceof Document))return;if(root instanceof HTMLImageElement)attach(root);root.querySelectorAll?.("img[data-media-asset-id][data-media-replace-url]").forEach(attach);}
 scan(document);new MutationObserver(records=>records.forEach(r=>r.addedNodes.forEach(n=>{if(n.nodeType===Node.ELEMENT_NODE)scan(n);}))).observe(document.documentElement,{childList:true,subtree:true});
})();