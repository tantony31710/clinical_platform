import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

const BASE_PAIRS = 40
const HELIX_RADIUS = 1.2
const HELIX_HEIGHT = 8
const SPHERE_RADIUS = 0.12

function HelixStrand() {
  const groupRef = useRef<THREE.Group>(null!)

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.003
    }
  })

  const nucleotidesA: JSX.Element[] = []
  const nucleotidesB: JSX.Element[] = []
  const rungs: JSX.Element[] = []

  for (let i = 0; i < BASE_PAIRS; i++) {
    const t = (i / BASE_PAIRS) * Math.PI * 4          // two full turns
    const y = (i / BASE_PAIRS) * HELIX_HEIGHT - HELIX_HEIGHT / 2

    const ax = Math.cos(t) * HELIX_RADIUS
    const az = Math.sin(t) * HELIX_RADIUS
    const bx = Math.cos(t + Math.PI) * HELIX_RADIUS   // opposite strand
    const bz = Math.sin(t + Math.PI) * HELIX_RADIUS

    // Strand A — cyan
    nucleotidesA.push(
      <mesh key={`a${i}`} position={[ax, y, az]}>
        <sphereGeometry args={[SPHERE_RADIUS, 8, 8]} />
        <meshStandardMaterial color="#2dd4bf" emissive="#2dd4bf" emissiveIntensity={0.4} />
      </mesh>
    )

    // Strand B — blue
    nucleotidesB.push(
      <mesh key={`b${i}`} position={[bx, y, bz]}>
        <sphereGeometry args={[SPHERE_RADIUS, 8, 8]} />
        <meshStandardMaterial color="#3b82f6" emissive="#3b82f6" emissiveIntensity={0.4} />
      </mesh>
    )

    // Base pair rung (cylinder connecting A to B)
    const mid = new THREE.Vector3((ax + bx) / 2, y, (az + bz) / 2)
    const dir = new THREE.Vector3(bx - ax, 0, bz - az)
    const len = dir.length()
    const quat = new THREE.Quaternion()
    quat.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize())

    // Alternate rung colours for visual rhythm
    const rungColor = i % 2 === 0 ? '#5eead4' : '#60a5fa'

    rungs.push(
      <mesh key={`r${i}`} position={[mid.x, mid.y, mid.z]} quaternion={quat}>
        <cylinderGeometry args={[0.025, 0.025, len, 6]} />
        <meshStandardMaterial color={rungColor} transparent opacity={0.55} />
      </mesh>
    )
  }

  return (
    <group ref={groupRef}>
      {nucleotidesA}
      {nucleotidesB}
      {rungs}
    </group>
  )
}

export default function DNAHelix3D() {
  return (
    <div style={{ width: '100%', height: 350 }}>
      <Canvas
        camera={{ position: [0, 0, 7], fov: 50 }}
        gl={{ alpha: true, antialias: true }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.4} />
        <pointLight position={[4, 4, 4]} intensity={1.2} color="#2dd4bf" />
        <pointLight position={[-4, -4, 4]} intensity={0.8} color="#3b82f6" />
        <HelixStrand />
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate={false}
          minPolarAngle={Math.PI / 4}
          maxPolarAngle={Math.PI * 0.75}
        />
      </Canvas>
    </div>
  )
}
