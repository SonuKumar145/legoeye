/**
 * @type {import('next').NextConfig}
 */

const nextConfig = {
  /* config options here */
  output: 'export',
    typescript: {
    // WARNING: this will let you build/deploy even with type errors!
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
