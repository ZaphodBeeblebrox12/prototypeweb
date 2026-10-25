/* Production image changes require server-authorised Django config. Static preview mode is local-only. */
(() => {
 "use strict";
 const config=window.TRADETHESIS_MEDIA_EDITOR,previewOnly=window.TRADETHESIS_MEDIA_PREVIEW_ONLY===true,serverEnabled=!!(config&&config.enabled===true&&config.csrfToken);
 if(!previewOnly&&!serverEnabled)return;
 const maxBytes=Number(config&&config.maxBytes)>0?Number(config.maxBytes):10*1024*1024;
 const allowedTypes=new Set(["image/jpeg","image/png","image/webp"]),attached=new WeakSet(),previewReplacements=new Map();
 function status(node,message,error){node.textContent=message;node.dataset.state=error?"error":"info";}
 function updateAllImages(assetId,url,alt){document.querySelectorAll("img[data-media-asset-id]").forEach(target=>{if(target.dataset.mediaAssetId!==assetId)return;target.src=url;target.removeAttribute("srcset");if(typeof alt==="string")target.alt=alt;});}
 function getReplaceUrl(img){if(img.dataset.mediaReplaceUrl)return img.dataset.mediaReplaceUrl;if(config&&typeof config.replaceUrlTemplate==="string"&&config.replaceUrlTemplate.includes("__ASSET_ID__"))return config.replaceUrlTemplate.replace("__ASSET_ID__",encodeURIComponent(img.dataset.mediaAssetId));return "";}
 function attach(img){
  if(!(img instanceof HTMLImageElement)||attached.has(img)||!img.dataset.mediaAssetId)return;
  const replaceUrl=getReplaceUrl(img);if(serverEnabled&&!replaceUrl)return;
  attached.add(img);const figure=img.closest("figure")||img.parentElement;if(!figure)return;
  if(previewReplacements.has(img.dataset.mediaAssetId))img.src=previewReplacements.get(img.dataset.mediaAssetId);
  const bar=document.createElement("div");bar.className="tt-media-replace-control";
  const btn=document.createElement("button");btn.type="button";btn.className="tt-media-replace-button";btn.textContent=serverEnabled?"Replace image":"Replace image (preview)";btn.setAttribute("aria-label","Replace this course image");
  const msg=document.createElement("span");msg.className="tt-media-replace-status";msg.setAttribute("role","status");msg.setAttribute("aria-live","polite");
  const input=document.createElement("input");input.type="file";input.accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp";input.hidden=true;input.tabIndex=-1;
  bar.append(btn,msg,input);const action=figure.querySelector(".course-reference-actions");if(action)action.append(bar);else img.insertAdjacentElement("afterend",bar);
  if(!serverEnabled)status(msg,"Local preview only — Django upload is not connected.",false);
  btn.addEventListener("click",()=>{if(!btn.disabled)input.click();});
  input.addEventListener("change",async()=>{
   const file=input.files&&input.files[0];if(!file)return;
   if(!allowedTypes.has(file.type)){status(msg,"Choose a JPG, PNG or WebP image.",true);input.value="";return;}
   if(file.size<=0||file.size>maxBytes){status(msg,"The image must be smaller than "+Math.round(maxBytes/1048576)+" MB.",true);input.value="";return;}
   btn.disabled=true;
   if(!serverEnabled){
    const reader=new FileReader();reader.onload=()=>{if(typeof reader.result!=="string"){status(msg,"The selected image could not be previewed.",true);btn.disabled=false;input.value="";return;}previewReplacements.set(img.dataset.mediaAssetId,reader.result);updateAllImages(img.dataset.mediaAssetId,reader.result);status(msg,"Preview only: image is changed in this open session, not uploaded or saved.",false);btn.disabled=false;input.value="";};
    reader.onerror=()=>{status(msg,"The selected image could not be read.",true);btn.disabled=false;input.value="";};reader.readAsDataURL(file);return;
   }
   status(msg,"Uploading image…",false);const data=new FormData();data.append("image",file,file.name);data.append("asset_id",img.dataset.mediaAssetId);
   try{const response=await fetch(replaceUrl,{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":config.csrfToken,"Accept":"application/json"},body:data});let result={};try{result=await response.json();}catch(_){}
    if(!response.ok||result.ok!==true||typeof result.image_url!=="string")throw new Error(result.detail||"The image could not be replaced. Try again.");
    const url=new URL(result.image_url,window.location.href);if(!["http:","https:"].includes(url.protocol))throw new Error("The server returned an invalid image URL.");
    updateAllImages(img.dataset.mediaAssetId,url.href,result.alt);status(msg,"Image replaced and saved.",false);document.dispatchEvent(new CustomEvent("tradethesis:media-replaced",{detail:{assetId:img.dataset.mediaAssetId,imageUrl:url.href}}));
   }catch(err){status(msg,err&&err.message?err.message:"Upload failed. Please try again.",true);}finally{btn.disabled=false;input.value="";}
  });
 }
 function scan(root){if(!root||!(root instanceof Element||root instanceof Document))return;if(root instanceof HTMLImageElement)attach(root);root.querySelectorAll?.("img[data-media-asset-id]").forEach(attach);}
 scan(document);new MutationObserver(records=>records.forEach(r=>r.addedNodes.forEach(n=>{if(n.nodeType===Node.ELEMENT_NODE)scan(n);}))).observe(document.documentElement,{childList:true,subtree:true});
})();