import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const NameCard = () => {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 1000);
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setClearColor(0x1b1d21); // 背景色を設定
    mount.appendChild(renderer.domElement);
    
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;
    
    const textureLoader = new THREE.TextureLoader();
    const frontTexture = textureLoader.load('/public/namecard/meishi_tsumugu1515_omote.png');
    const backTexture = textureLoader.load('/public/namecard/meishi_tsumugu1515_ura.png');
    
    frontTexture.encoding = THREE.sRGBEncoding;
    backTexture.encoding = THREE.sRGBEncoding;
    
    const materials = [
      new THREE.MeshBasicMaterial({ color: 0xddd1ba }), // 左側面
      new THREE.MeshBasicMaterial({ color: 0xddd1ba }), // 右側面
      new THREE.MeshBasicMaterial({ color: 0xddd1ba }), // 上側面
      new THREE.MeshBasicMaterial({ color: 0xddd1ba }), // 下側面
      new THREE.MeshBasicMaterial({ map: frontTexture }), // 前面
      new THREE.MeshBasicMaterial({ map: backTexture }) // 背面
    ];
    
    const geometry = new THREE.BoxGeometry(3, 2, 0.01); // 名刺のサイズと厚み
    const card = new THREE.Mesh(geometry, materials);
    scene.add(card);
    
    camera.position.z = 10; // 初期位置を遠くに設定
    function animate() {
      requestAnimationFrame(animate);
      
      // カメラのズームインアニメーション
      if (camera.position.z > 1.8) {
        camera.position.z -= 0.1;
      }
      
      controls.update();
      renderer.render(scene, camera);
    }
    
    animate();
    
    return () => {
      mount.removeChild(renderer.domElement);
    };
  }, []);
  
  return <div className='NameCardWrapper' ref={mountRef} style={{ width: '50%', aspectRatio: '3 / 2', cursor: 'grab' }} />;
};

export default NameCard;